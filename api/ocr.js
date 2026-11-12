const path=require('path');
const {createWorker}=require('tesseract.js');
module.exports=async function handler(req,res){
 res.setHeader('Cache-Control','no-store');
 if(req.method!=='POST')return res.status(405).json({error:'Use POST'});
 let worker;
 try{
  const payload=typeof req.body==='string'?JSON.parse(req.body):req.body;
  const match=/^data:(image\/(?:png|jpeg|webp|bmp|tiff));base64,([A-Za-z0-9+/=]+)$/.exec(payload?.image_data||'');
  if(!match)return res.status(400).json({error:'Provide a supported image'});
  const bytes=Buffer.from(match[2],'base64');
  if(!bytes.length||bytes.length>3*1024*1024)return res.status(413).json({error:'Hosted OCR supports images up to 3 MB'});
  const hex=bytes.subarray(0,12).toString('hex');const valid={'image/png':hex.startsWith('89504e470d0a1a0a'),'image/jpeg':hex.startsWith('ffd8ff'),'image/webp':bytes.subarray(0,4).toString()==='RIFF'&&bytes.subarray(8,12).toString()==='WEBP','image/bmp':hex.startsWith('424d'),'image/tiff':hex.startsWith('49492a00')||hex.startsWith('4d4d002a')};
  if(!valid[match[1]])return res.status(400).json({error:'Image type does not match its contents'});
  worker=await createWorker('eng',1,{langPath:path.join(process.cwd(),'models'),gzip:false,cacheMethod:'none'});
  const {data}=await worker.recognize(bytes);
  return res.status(200).json({text:data.text.trim(),confidence:data.confidence,quality_warning:'Check extracted text against the image and correct any omissions before using the result.'});
 }catch(e){return res.status(422).json({error:'Could not read this image. Try a clearer image or paste its copy.'});}
 finally{if(worker)await worker.terminate();}
};
