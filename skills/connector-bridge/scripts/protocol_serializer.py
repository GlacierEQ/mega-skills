#!/usr/bin/env python3
"""
Protocol Serializer
Normalizes payloads for PostgREST, REST, GraphQL, JSON-RPC protocols.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


class Protocol(Enum):
    POSTGREST = "postgrest"
    REST = "rest"
    GRAPHQL = "graphql"
    JSON_RPC = "jsonrpc"


@dataclass
class SerializedRequest:
    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[str]
    params: Optional[Dict[str, Any]]


class BaseSerializer(ABC):
    """Base class for protocol serializers."""
    
    @abstractmethod
    def serialize(self, operation: str, payload: Dict[str, Any], config: Dict) -> SerializedRequest:
        pass
    
    @abstractmethod
    def deserialize(self, response: Dict, operation: str) -> Dict:
        pass


class PostgRESTSerializer(BaseSerializer):
    """Serializer for PostgREST (Supabase) API."""
    
    def serialize(self, operation: str, payload: Dict[str, Any], config: Dict) -> SerializedRequest:
        base_url = config.get("base_url", "").rstrip("/")
        table = payload.get("table", "")
        
        if operation == "select":
            columns = payload.get("columns", "*")
            filters = payload.get("filters", {})
            order = payload.get("order", "")
            limit = payload.get("limit", "")
            
            url = f"{base_url}/{table}?select={columns}"
            if filters:
                filter_str = "&".join(f"{k}=eq.{v}" for k, v in filters.items())
                url += f"&{filter_str}"
            if order:
                url += f"&order={order}"
            if limit:
                url += f"&limit={limit}"
            
            return SerializedRequest(
                method="GET",
                url=url,
                headers=self._auth_headers(config),
                body=None,
                params=None
            )
        
        elif operation in ("insert", "upsert"):
            data = payload.get("data", {})
            on_conflict = payload.get("on_conflict", "")
            
            url = f"{base_url}/{table}"
            if on_conflict:
                url += f"?on_conflict={on_conflict}"
            
            return SerializedRequest(
                method="POST",
                url=url,
                headers={**self._auth_headers(config), "Content-Type": "application/json", "Prefer": "return=representation"},
                body=json.dumps(data),
                params=None
            )
        
        elif operation in ("update", "patch"):
            data = payload.get("data", {})
            filters = payload.get("filters", {})
            
            url = f"{base_url}/{table}"
            if filters:
                filter_str = "&".join(f"{k}=eq.{v}" for k, v in filters.items())
                url += f"?{filter_str}"
            
            return SerializedRequest(
                method="PATCH",
                url=url,
                headers={**self._auth_headers(config), "Content-Type": "application/json", "Prefer": "return=representation"},
                body=json.dumps(data),
                params=None
            )
        
        elif operation == "delete":
            filters = payload.get("filters", {})
            
            url = f"{base_url}/{table}"
            if filters:
                filter_str = "&".join(f"{k}=eq.{v}" for k, v in filters.items())
                url += f"?{filter_str}"
            
            return SerializedRequest(
                method="DELETE",
                url=url,
                headers=self._auth_headers(config),
                body=None,
                params=None
            )
        
        else:
            raise ValueError(f"Unknown PostgREST operation: {operation}")
    
    def deserialize(self, response: Dict, operation: str) -> Dict:
        return response
    
    def _auth_headers(self, config: Dict) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if config.get("api_key"):
            headers["apikey"] = config["api_key"]
            headers["Authorization"] = f"Bearer {config['api_key']}"
        return headers


class RESTSerializer(BaseSerializer):
    """Serializer for generic REST APIs."""
    
    def serialize(self, operation: str, payload: Dict[str, Any], config: Dict) -> SerializedRequest:
        base_url = config.get("base_url", "").rstrip("/")
        endpoint = payload.get("endpoint", "")
        method = payload.get("method", "GET").upper()
        
        url = f"{base_url}/{endpoint}".replace("//", "/").replace(":/", "://")
        
        headers = {"Accept": "application/json"}
        if config.get("api_key"):
            headers["Authorization"] = f"Bearer {config['api_key']}"
        if config.get("api_key_header"):
            headers[config["api_key_header"]] = config["api_key"]
        
        body = None
        params = None
        
        if method in ("POST", "PUT", "PATCH"):
            body = json.dumps(payload.get("data", {}))
            headers["Content-Type"] = "application/json"
        elif method == "GET":
            params = payload.get("params", {})
        
        return SerializedRequest(
            method=method,
            url=url,
            headers=headers,
            body=body,
            params=params
        )
    
    def deserialize(self, response: Dict, operation: str) -> Dict:
        return response


class GraphQLSerializer(BaseSerializer):
    """Serializer for GraphQL APIs."""
    
    def serialize(self, operation: str, payload: Dict[str, Any], config: Dict) -> SerializedRequest:
        base_url = config.get("base_url", "").rstrip("/")
        
        query = payload.get("query", "")
        variables = payload.get("variables", {})
        operation_name = payload.get("operation_name", "")
        
        body = {"query": query}
        if variables:
            body["variables"] = variables
        if operation_name:
            body["operationName"] = operation_name
        
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if config.get("api_key"):
            headers["Authorization"] = f"Bearer {config['api_key']}"
        
        return SerializedRequest(
            method="POST",
            url=base_url,
            headers=headers,
            body=json.dumps(body),
            params=None
        )
    
    def deserialize(self, response: Dict, operation: str) -> Dict:
        if "errors" in response:
            return {"errors": response["errors"]}
        return response.get("data", response)


class JSONRPCSerializer(BaseSerializer):
    """Serializer for JSON-RPC 2.0."""
    
    def __init__(self):
        self.request_id = 0
    
    def serialize(self, operation: str, payload: Dict[str, Any], config: Dict) -> SerializedRequest:
        base_url = config.get("base_url", "").rstrip("/")
        
        self.request_id += 1
        body = {
            "jsonrpc": "2.0",
            "method": operation,
            "params": payload.get("params", []),
            "id": self.request_id
        }
        
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if config.get("api_key"):
            headers["Authorization"] = f"Bearer {config['api_key']}"
        
        return SerializedRequest(
            method="POST",
            url=base_url,
            headers=headers,
            body=json.dumps(body),
            params=None
        )
    
    def deserialize(self, response: Dict, operation: str) -> Dict:
        if "error" in response:
            return {"error": response["error"]}
        return response.get("result", response)


SERIALIZERS = {
    Protocol.POSTGREST: PostgRESTSerializer(),
    Protocol.REST: RESTSerializer(),
    Protocol.GRAPHQL: GraphQLSerializer(),
    Protocol.JSON_RPC: JSONRPCSerializer(),
}


def get_serializer(protocol: Union[Protocol, str]) -> BaseSerializer:
    """Get serializer for protocol."""
    if isinstance(protocol, str):
        protocol = Protocol(protocol.lower())
    return SERIALIZERS[protocol]


def main():
    if len(sys.argv) < 3:
        print("Usage: protocol_serializer.py <protocol> <operation> [payload_json] [config_json]")
        print("Protocols: postgrest, rest, graphql, jsonrpc")
        sys.exit(1)
    
    protocol = Protocol(sys.argv[1].lower())
    operation = sys.argv[2]
    payload = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    config = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
    
    serializer = get_serializer(protocol)
    request = serializer.serialize(operation, payload, config)
    
    print(json.dumps({
        "method": request.method,
        "url": request.url,
        "headers": request.headers,
        "body": request.body,
        "params": request.params
    }, indent=2))


if __name__ == "__main__":
    main()
