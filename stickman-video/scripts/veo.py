import json,os,sys,time,base64,urllib.request,urllib.error
K=os.environ['GEMINI_API_KEY']; B='https://generativelanguage.googleapis.com/v1beta/'
img,prompt,out=sys.argv[1],sys.argv[2],sys.argv[3]; model=sys.argv[4] if len(sys.argv)>4 else 'veo-3.1-lite-generate-preview'
def req(u,body=None):
    r=urllib.request.Request(u,json.dumps(body).encode() if body else None,{'Content-Type':'application/json','x-goog-api-key':K})
    try: return json.loads(urllib.request.urlopen(r,timeout=120).read())
    except urllib.error.HTTPError as e: print('HTTP',e.code,e.read().decode()[:500]); sys.exit(1)
body={'instances':[{'prompt':prompt,'image':{'bytesBase64Encoded':base64.b64encode(open(img,'rb').read()).decode(),'mimeType':'image/png'}}],
      'parameters':{'aspectRatio':'16:9', **({'durationSeconds':int(os.environ['VEO_DUR'])} if os.environ.get('VEO_DUR') else {})}}
op=req(B+f'models/{model}:predictLongRunning',body); print('op',op.get('name','?')[-20:],flush=True); t0=time.time()
while not op.get('done'):
    time.sleep(10); op=req(B+op['name'])
    if time.time()-t0>600: print('timeout'); sys.exit(1)
if 'error' in op: print('error',op['error']); sys.exit(1)
res=op['response']; print('keys',list(res.keys()))
samples=res.get('generateVideoResponse',res).get('generatedSamples') or res.get('generatedVideos')
uri=samples[0]['video']['uri']
r=urllib.request.Request(uri,headers={'x-goog-api-key':K}); open(out,'wb').write(urllib.request.urlopen(r,timeout=300).read())
print('saved',out,round(time.time()-t0),'s')
