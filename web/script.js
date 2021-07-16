let cont = document.getElementById("container")
let img = document.getElementById("image")
let imgL = document.getElementById("imageLabel")
let text = document.getElementById("text")
let action = document.getElementById("action")
let type = document.getElementById("type")
let btn = document.getElementById("btn")
let filename = document.getElementById("filename")
let check = document.getElementById("check")
let cancel = document.getElementById("cancel")

cancel.addEventListener("click", () => {
    // clear the form
    document.getElementById("form").reset()
})
btn.addEventListener("click", (event) => {
    event.preventDefault()
    if (!check.checked) {
        throw new Error("You must agree our terms and conditions!")
    }
    if (action.value === "" || type.value === "" || cont.files.length === 0) {
        throw new Error("You must provide approriate option!")
    }
    if (action.value === "IMAGE" && img.files.length > 0) {
        throw new Error("You must provide appropriate option!")
    }

    let body = new FormData()
    body.append("type", type.value)
    body.append("container", cont.files[0])
    if (action.value === "ENCODE") {
        switch (type.value) {
            case "IMAGE":
                body.append("data", img.files[0])
                break
            case "MESSAGE":
                body.append("data", text.value)
                break
        }
        encode(body)
    }
    if (action.value === "DECODE") {
        decode(body)
    }
})

function encode(body) {
    return fetch("/encode", {
        method: 'POST',
        body: body
    })
        .then((res) => {
            if (res.status === 500) {
                throw new Error("Request format is wrong!")
            }
            if (res.status === 401) {
                throw new Error("Data is too big, cannot hide into container!")
            }
            return res.blob()
        })
        .then(blob => {
            saveFile(blob, filename.value)
            cancel.click()
        })
        .catch(err => {
            console.log(err)
            alert(err.message)
        })
}

function decode(body) {
    return fetch("/decode", {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        body: body
    })
        .then((res) => {
            if (res.status === 500) {
                throw new Error("Data format wrong, decoding fail!")
            }

            return res.blob()
        })
        .then(blob => {
            if (body.type === "IMAGE") {
                saveFile(blob,`${filename.value}.png`)
                cancel.click()
            }
            if (type.value === "MESSAGE") {
                saveFile(blob,`${filename.value}.txt`)
                cancel.click()
            }
        })
        .catch(err => {
            console.log(err)
            alert(err.message)
        })
}
function saveFile(blob, filename) {
    let url = window.URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a); // we need to append the element to the dom -> otherwise it will not work in firefox
    a.click();
    a.remove();
}

action.addEventListener("change", () => {
    if (action.value === 'DECODE') {
        text.disabled = true
        img.disabled = true
        imgL.innerHTML = "Disabled"
    } else {
        text.disabled = false
        img.disabled = false
        imgL.innerHTML = "Loading data as image"
    }
})
type.addEventListener("change", () => {
    if (action.value === 'ENCODE') {
        switch (type.value) {
            case "IMAGE":
                text.disabled = true
                img.disabled = false
                imgL.innerHTML = "Loading data as image"
                break;
            case "MESSAGE":
                text.disabled = false
                img.disabled = true
                imgL.innerHTML = "Disabled"
        }
    }
})
