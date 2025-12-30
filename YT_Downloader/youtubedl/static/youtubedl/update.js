async function GetProgress(){
    let url = window.location.href
    let splitUrl = url.split("/")
    let video_id = Number(splitUrl[splitUrl.length - 1])
    let current_progress = await fetch('http://localhost:8000/api/progress/' + video_id)
        .then((response)=>{
            if(response.ok){
                return response.text();
            }
            else{
                throw new Error('Something went wrong!');
            }
        })
        .then(async (data)=>{
            let jsonData = JSON.parse(data)
            let progress = Number(jsonData.progress);
            let progressBar = document.getElementById("pb");
            progressBar.style.width = progress + "%";

            let statusText = document.getElementById("status");
            statusText.innerText = jsonData.status;

            let progressValue = document.getElementById("progress");
            progressValue.innerText = progress + "%";

            let downloadButton = document.getElementById("downloadButton");
            downloadButton.disabled = progress < 100
            return progress
        })
        .catch((error)=>{
            console.error(error);
        });
    return current_progress;
}

let updater = setInterval(async () =>{
    let current_progress = await GetProgress()
    if(current_progress >= 100){
        clearInterval(updater)
    }
}, 500)