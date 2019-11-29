console.log('Hello TensorFlow');
console.log('This is to use CNN SR');



async function run() {  
    const model = await tf.loadLayersModel('../models/model.json');
    console.log("model loaded");
}

document.addEventListener('DOMContentLoaded', run);
