// Cloudflare Worker gateway for Custom GPT Actions.
// Required: secret API_KEY, secret GH_TOKEN; vars GH_OWNER and GH_REPO.
// Restrict access with a bearer token. Do NOT expose GitHub credentials in GPT instructions.
const result=(body,status=200)=>new Response(JSON.stringify(body),{
  status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store"}
});
export default {
  async fetch(request,env) {
    if(!env.API_KEY || request.headers.get("authorization")!=="Bearer "+env.API_KEY)
      return result({error:"Unauthorized"},401);
    if(!env.GH_TOKEN || !env.GH_OWNER || !env.GH_REPO)
      return result({error:"Gateway is not configured"},503);
    const url=new URL(request.url);
    const api="https://api.github.com/repos/"+env.GH_OWNER+"/"+env.GH_REPO;
    const headers={"Authorization":"Bearer "+env.GH_TOKEN,"Accept":"application/vnd.github+json",
      "X-GitHub-Api-Version":"2022-11-28","User-Agent":"SGS-Steam-Auto-Video"};
    if(url.pathname==="/create" && request.method==="POST") {
      let payload;
      try {payload=await request.json()} catch {return result({error:"Invalid JSON"},400)}
      const app=String(payload.app_id||"");
      if(!/^\d{3,10}$/.test(app))return result({error:"Invalid Steam App ID"},400);
      const requestId=crypto.randomUUID();
      const response=await fetch(api+"/actions/workflows/create-video.yml/dispatches",{
        method:"POST",headers:{...headers,"content-type":"application/json"},
        body:JSON.stringify({ref:"main",inputs:{app_id:app,request_id:requestId}})
      });
      if(!response.ok)return result({error:"Dispatch failed",status:response.status,detail:(await response.text()).slice(0,250)},502);
      return result({status:"queued",app_id:app,request_id:requestId,workflow_url:"https://github.com/"+env.GH_OWNER+"/"+env.GH_REPO+"/actions"},202);
    }
    if(url.pathname==="/status" && request.method==="GET") {
      const app=url.searchParams.get("app_id")||"";
      const requestId=url.searchParams.get("request_id")||"";
      if(!/^\d{3,10}$/.test(app)|| !/^[0-9a-f-]{36}$/.test(requestId))
        return result({error:"Invalid identifiers"},400);
      const r=await fetch(api+"/releases/tags/sgs-"+app+"-"+requestId,{headers});
      if(r.status===404)return result({status:"not_ready",app_id:app,request_id:requestId});
      if(!r.ok)return result({error:"Lookup failed",status:r.status},502);
      const release=await r.json();
      const mp4=release.assets?.find(a=>a.name==="SGS_10sec.mp4");
      return result({status:mp4?"ready":"not_ready",app_id:app,request_id:requestId,
        mp4_url:mp4?.browser_download_url||null,release_url:release.html_url});
    }
    return result({error:"Not found"},404);
  }
};
