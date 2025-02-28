// ... (keep existing code until container_request function) ...

function container_request(challenge_id) {
    var path = "/containers/api/request";
    var requestButton = document.getElementById("container-request-btn");
    var requestResult = document.getElementById("container-request-result");
    var connectionInfo = document.getElementById("container-connection-info");
    var containerExpires = document.getElementById("container-expires");
    var containerExpiresTime = document.getElementById("container-expires-time");
    var requestError = document.getElementById("container-request-error");

    requestButton.setAttribute("disabled", "disabled");

    var xhr = new XMLHttpRequest();
    xhr.open("POST", path, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("CSRF-Token", init.csrfNonce);
    xhr.send(JSON.stringify({ chal_id: challenge_id }));

    xhr.onload = function () {
        var data = JSON.parse(this.responseText);
        if (data.error !== undefined) {
            requestError.style.display = "";
            requestError.firstElementChild.innerHTML = data.error;
            requestButton.removeAttribute("disabled");
        } else if (data.message !== undefined) {
            requestError.style.display = "";
            requestError.firstElementChild.innerHTML = data.message;
            requestButton.removeAttribute("disabled");
        } else {
            requestError.style.display = "none";
            requestError.firstElementChild.innerHTML = "";
            requestButton.parentNode.removeChild(requestButton);

            // Create connection info HTML for multiple ports
            var connectionHtml = '<div class="container-ports">';
            Object.entries(data.ports).forEach(([internal_port, external_port]) => {
                if (data.hostname.startsWith("http")) {
                    connectionHtml += `<p><strong>Port ${internal_port}:</strong> <a href="${data.hostname}:${external_port}" target="_blank">${data.hostname}:${external_port}</a></p>`;
                } else {
                    connectionHtml += `<p><strong>Port ${internal_port}:</strong> ${data.hostname} ${external_port}</p>`;
                }
            });
            connectionHtml += '</div>';
            
            connectionInfo.innerHTML = connectionHtml;
            containerExpires.innerHTML = Math.ceil((new Date(data.expires * 1000) - new Date()) / 1000 / 60);
            containerExpiresTime.style.display = "";
            requestResult.style.display = "";
        }
        console.log(data);
    };
}

// ... (keep rest of the file unchanged) ...
