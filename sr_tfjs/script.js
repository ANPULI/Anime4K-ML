console.log('Hello TensorFlow');
console.log('This is to use CNN SR');



async function run() {  
    const model = await tf.loadLayersModel('https://foo.bar/tfjs_artifacts/model.json');
}

document.addEventListener('DOMContentLoaded', run);
