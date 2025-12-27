const fullEmailSection = document.querySelector(".full-email-section");
const emailList = document.querySelector(".email-list");
let activeEmailId = null;
let previouslyClickedEmail = null;

Array.from(emailList.children).forEach(email => {
    if (email.dataset.emailStatus === "READ")
    {
        email.classList.add("read");
    }
})

emailList.addEventListener("click", async (e) => {
    const emailEl = e.target.closest(".email-item");
    if (!emailEl) return;
    
    const emailId = emailEl.dataset.emailId;
    let emailStatus = emailEl.dataset.emailStatus;

    try{
        await loadEmailPreview(emailId);

        if (emailStatus === "UNREAD"){
            markEmailAsRead(emailEl, emailId);
        }
        
        selectEmail(emailEl);
    }catch (err)
    {
        console.error("Failed to load email", err);
    }
    
    fullEmailSection.style.visibility = "visible";
    previouslyClickedEmail = emailEl;
    loadEmailPreview(emailId)
});

function markEmailAsRead(emailEl, emailId){
    emailEl.dataset.emailStatus = "READ";
    emailEl.classList.add("read");
    emailEl.classList.add("was-unread-when-selected");
    changeEmailStatus(emailId, "READ");
}

function selectEmail(emailEl)
{
    if (previouslyClickedEmail)
    {
        previouslyClickedEmail.classList.remove("selected");
        previouslyClickedEmail.classList.remove("was-unread-when-selected");
    }
    emailEl.classList.add("selected");
    previouslyClickedEmail = emailEl;
}

async function loadEmailPreview(emailId){
    activeEmailId = emailId;

    const res = await fetch(`/email/${emailId}`)
    if (!res.ok) throw new Error("Fetch failed!");

    const data = await res.json()
    
    if (emailId !== activeEmailId) return;

    document.querySelector("#preview-sender").textContent = data.sender;
    document.querySelector("#preview-date").textContent = data.date;
    document.querySelector("#preview-body").textContent = data.body;
    document.querySelector("#preview-subject").textContent = data.subject;
}

async function changeEmailStatus(id, emailStatus) {
    const data = {
        email_id : id,
        email_status: emailStatus
    };
    fetch('/api/submit-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok){
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
    // Handle the data from the backend
    console.log('Success:', data);
    console.log('Data sent successfully!');
    })
    .catch((error) => {
        // Handle errors during the fetch operation
        console.error('Error:', error);
        alert('Failed to send data.');
    });
}