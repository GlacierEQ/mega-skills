#!/usr/bin/env node
"use strict";
/** Live loopback HTTP conformance, against built pinned Supermemory SDK (no external writes). */
const assert = require("node:assert/strict");
const http = require("node:http");
const path = require("node:path");
const { once } = require("node:events");
const sdkRoot = process.argv[2] || process.env.SDK_ROOT;
if (!sdkRoot) throw new Error("SDK_ROOT or first argument required");
const sdk = require(path.resolve(sdkRoot, "dist", "index.js"));
const Supermemory = sdk.default || sdk.Supermemory;
let attempts = 0;
const events = [];
const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://127.0.0.1");
  const authPresent = Boolean(req.headers.authorization);
  events.push({method: req.method, path: url.pathname, authPresent});
  if (url.pathname === "/slow") return void setTimeout(() => {
    if (!res.destroyed) { res.writeHead(200, {"content-type":"application/json"}); res.end('{"slow":true}'); }
  }, 700);
  let status = 200;
  if (url.pathname === "/unauthorized") status = 401;
  if (url.pathname === "/rate-limit") status = 429;
  if (url.pathname === "/server-error") status = 503;
  if (url.pathname === "/flaky") { attempts++; if (attempts <= 2) status = 503; }
  const payload = status === 200 ? {ok:true, path:url.pathname} : {error:{message:"controlled failure",type:"test"}};
  res.writeHead(status, {"content-type":"application/json", "x-request-id":"loopback-test-" + status});
  res.end(JSON.stringify(payload));
});
function client(baseURL, opts={}) {
  return new Supermemory({baseURL, apiKey:"sdk-master-loopback-only", maxRetries:0, timeout:500, ...opts});
}
async function errorStatus(promise, expected, label) {
  let failure;
  try {await promise;} catch (error) {failure=error;}
  assert(failure, label + ": SDK must reject");
  assert.equal(failure.status, expected, label + ": status");
  events.push({assertion:label, errorName:failure.name, status:failure.status});
}
async function main() {
  server.listen(0,"127.0.0.1");
  await once(server,"listening");
  const baseURL = "http://127.0.0.1:" + server.address().port;
  try {
    const c=client(baseURL);
    const good=await c.get("/success");
    assert.deepEqual(good,{ok:true,path:"/success"});
    await errorStatus(c.get("/unauthorized"),401,"auth");
    await errorStatus(c.get("/rate-limit"),429,"rate-limit");
    await errorStatus(c.get("/server-error"),503,"server-error");
    const cRetry=client(baseURL,{maxRetries:2,timeout:5000});
    const recovered=await cRetry.get("/flaky");
    assert.equal(recovered.ok,true);
    assert.equal(attempts,3,"bounded retries must be 2 after first attempt");
    const cTimeout=client(baseURL,{timeout:30,maxRetries:0});
    let timedOut;
    try {await cTimeout.get("/slow");} catch (err) {timedOut=err;}
    assert(timedOut,"timeout must reject");
    assert.equal(timedOut.name,"APIConnectionTimeoutError","timeout classification");
    const ctl=new AbortController();
    const p=c.get("/slow",{signal:ctl.signal});
    setTimeout(()=>ctl.abort(),20);
    let aborted;
    try {await p;} catch(err) {aborted=err;}
    assert(aborted,"abort must reject");
    assert.equal(aborted.name,"APIUserAbortError","abort classification");
    assert(events.every(e=>!("path" in e)||e.authPresent),"all HTTP requests carry configured auth header");
    console.log(JSON.stringify({status:"PASS",sdkRevision:process.env.SDK_REVISION||"unknown",positive:true,errorStatuses:[401,429,503],retriedAttempts:attempts,timeout:timedOut.name,abort:aborted.name,httpRequests:events.filter(e=>e.path).length,mode:"real HTTP loopback, no provider mutation"},null,2));
  } finally {
    server.closeAllConnections();
    await new Promise(resolve=>server.close(resolve));
  }
}
main().catch(e=>{console.error("CONFORMANCE_FAIL:",e.stack||e);process.exitCode=1;server.closeAllConnections();server.close();});
