const fullEmailSection = document.querySelector(".full-email-section");
const emailList = document.querySelector(".email-list");

const filterBtn = document.getElementById("filter-btn");
const applyFiltersBtn = document.getElementById("apply-filters");
const filterModal = document.getElementById("filter-modal");
let currentFilters = {
    category: "",
    priority: ""
};

let activeEmailId = null;
let previouslyClickedEmail = null;
let offset = 0;
const limit = 20;
let isLoading = false;
let hasMore = true;

loadEmails();

async function loadEmails()
{
    if (isLoading || !hasMore) return;

    isLoading = true;

    const params = new URLSearchParams({
        offset,
        limit, 
        category: currentFilters.category,
        priority: currentFilters.priority
    })

    const res = await fetch(`/emails?${params.toString()}`);
    const emails = await res.json();

    if (emails.length === 0){
        hasMore = false;
        isLoading = false;
        return;
    }

    emails.forEach(email => renderEmails(email));
    offset += limit;
    isLoading = false;
}

function renderEmails(email)
{
    const emailItem = document.createElement("div");
    emailItem.classList.add("email-item");
    emailItem.dataset.emailId = email[0];
    emailItem.dataset.emailStatus = email[5]

    if (email[5] === "READ") {
        emailItem.classList.add("read");
    }

    if (email[3] === null)
    {
        email[3] = "None";
    }

    priority_colours = {
        "low" : "#397025ff",
        "normal" : "#b39a2cff",
        "high" : "#C41E3A"
    };

    const date = new Date(email[6]);
    const options = {weekday: "short"};
    const day = date.toLocaleString('en-US', options);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');

    const formattedDate = `${day} ${hours}:${minutes}`

    emailItem.innerHTML = `
            <div class="profile-pic">
                <img id="profile-pic" src="/imgs/unknown.png" alt="">
            </div>
            <div class="email-content">
                <div class="sender-div">
                    <h3>${email[1]}</h3>
                    <p>${email[3]}</p>
                </div>
                <div class="subject-div">
                    <h4>${email[2]}</h4>
                    <p>${formattedDate}</p>
                </div>
                <div class="body-div">
                    <p>Lorem ipsum dolor sit amet consectetur adipisicing elit.</p>
                    <div class="priority-tag" style="color: ${priority_colours[email[4]]}">${email[4]}</div>
                </div>
            </div>
    `
    emailList.appendChild(emailItem);
}

const observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting)
    {
        loadEmails()
    }
}, {
    root: null,
    threshold: 0.1
});

observer.observe(document.getElementById("scroll-sentinel"));


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

filterBtn.addEventListener("click", (e) => {
    filterModal.classList.toggle("hidden");
})

filterModal.addEventListener("click", (e) => {
    if (e.target === filterModal){
        filterModal.classList.add("hidden");
    }
})

applyFiltersBtn.addEventListener("click", (e) => {
    currentFilters.category = document.getElementById("filter-category").value.toLowerCase();
    currentFilters.priority = document.getElementById("filter-priority").value.toLowerCase();

    offset = 0;
    hasMore = true;
    emailList.innerHTML = "";

    filterModal.classList.add("hidden");
    loadEmails()
})