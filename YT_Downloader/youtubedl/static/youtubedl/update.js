async function GetProgress(){
    let url = window.location.href
    let splitUrl = url.split("/")
    let video_id = Number(splitUrl[splitUrl.length - 1])
    let current_progress = await fetch('/api/progress/' + video_id)
        .then((response)=>{
            if(response.ok){
                return response.text();
            }
        })
        .then(async (data)=>{
            let jsonData = JSON.parse(data)
            let progress = Number(jsonData.progress);
            let progressBar = document.getElementById("pb");
            progressBar.style.width = progress + "%";
            
            let status = ""
            let continueLoop = true
            if (jsonData.status === "queued"){
                status = "In queue: " + jsonData.queue_position;
            }
            else if(jsonData.status === "downloading"){
                if(progress >= 100){
                    status = "Converting..."
                }
                else{
                    status = "Downloading: " + Math.floor(progress) + "%";
                }
            }
            else if(jsonData.status === "finished"){
                status = "Finished"
                continueLoop = false;

                let downloadButton = document.getElementById("downloadButton");
                downloadButton.disabled = false;
            }
            else {
                status = "Failed";
                continueLoop = false;
            }

            let progressValue = document.getElementById("progress");
            progressValue.innerText = status;
            
            return continueLoop;
        })
        .catch((error)=>{
            console.error(error);
        });
    return current_progress;
}

let updater = setInterval(async () =>{
    let continueLoop = await GetProgress()
    if(!continueLoop){
        clearInterval(updater)
    }
}, 500)