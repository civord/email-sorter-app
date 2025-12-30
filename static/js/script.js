document.addEventListener('DOMContentLoaded', () => {
    const backBtn = document.querySelector(".back-btn");
    const fullEmailSection = document.querySelector(".full-email-section");
    const emailList = document.querySelector(".email-list");
    const middlePaneSectionContainer = document.querySelector(".mid-container");
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

    async function loadEmails()
    {
        if (isLoading || !hasMore) return;

        isLoading = true;

        const params = new URLSearchParams();
        params.append('offset', offset);
        params.append('limit', limit);
        if (currentFilters.category) params.append('category', currentFilters.category);
        if (currentFilters.priority) params.append('priority', currentFilters.priority);

        try {
            const res = await fetch(`/emails?${params.toString()}`);
            const emails = await res.json();

            // No results -> we've exhausted the list
            if (!emails || emails.length === 0){
                hasMore = false;
                isLoading = false;
                return;
            }

            emails.forEach(email => renderEmails(email));

            // Advance by actual number of returned items (safer than fixed `limit`)
            offset += emails.length;

            // If server returned fewer than `limit`, we've reached the end
            if (emails.length < limit) {
                hasMore = false;
            }
        } catch (err) {
            console.error('loadEmails error', err);
        } finally {
            isLoading = false;
        }
    }

    async function renderEmails(email)
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

        const formattedDate = `${day} ${hours}:${minutes}`;

        const sender = email[1].split("<")[0];
        const sender_email = email[1].split("<")[1].replace('>', '').toLowerCase();
        const sender_hash = await sha256(sender_email);

        emailItem.innerHTML = `
                <div class="profile-pic">
                    <img id="profile-pic" src="https://www.gravatar.com/avatar/${sender_hash}?d=identicon" alt="">
                </div>
                <div class="email-content">
                    <div class="sender-div">
                        <h3>${sender}</h3>
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

    async function sha256(email) {
        const encoder = new TextEncoder();
        const data = encoder.encode(email);

        const hashBuffer = await crypto.subtle.digest("SHA-256", data);

        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
        return hashHex;
    }

    // Start loading after DOM ready
    loadEmails();

    // Use the scrolling container as the root. Add a rootMargin to help trigger earlier on mobile.
    const scrollRoot = document.querySelector('.middle-pane-section') || null;
    const observer = new IntersectionObserver(entries => {
        if (entries[0] && entries[0].isIntersecting) {
            loadEmails();
        }
    }, {
        root: scrollRoot,
        rootMargin: '0px 0px 200px 0px',
        threshold: 0.1
    });

    const sentinel = document.getElementById("scroll-sentinel");
    if (sentinel) {
        observer.observe(sentinel);
    }


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

        if (window.innerWidth <= 767)
        {
            middlePaneSectionContainer.classList.add("hidden");
            fullEmailSection.classList.remove("hidden");
            fullEmailSection.classList.add("active");
            backBtn.classList.add("active");
        }
        
        document.querySelector("#preview-sender").textContent = data.sender;
        document.querySelector("#preview-date").textContent = data.date;
        document.querySelector("#preview-body").textContent = data.body;
        document.querySelector("#preview-subject").textContent = data.subject;
        document.querySelector("#full-profile-pic").src = `https://gravatar.com/avatar/${data["sender_hash"]}?d=identicon`
    }

    backBtn && backBtn.addEventListener("click", (e) => {
        middlePaneSectionContainer.classList.remove("hidden");
        fullEmailSection.classList.add("hidden");
        fullEmailSection.classList.remove("active");
        backBtn.classList.remove("active");
        activeEmailId = 0;
        if (previouslyClickedEmail) {
            previouslyClickedEmail.classList.remove("selected");
            previouslyClickedEmail.classList.remove("was-unread-when-selected");
            previouslyClickedEmail = null;
        }
        backBtn.classList.remove("active");
    })


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
        console.log('Success:', data);
        console.log('Data sent successfully!');
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Failed to send data.');
        });
    }

    filterBtn && filterBtn.addEventListener("click", (e) => {
        filterModal.classList.toggle("hidden");
    })

    filterModal && filterModal.addEventListener("click", (e) => {
        if (e.target === filterModal){
            filterModal.classList.add("hidden");
        }
    })

    applyFiltersBtn && applyFiltersBtn.addEventListener("click", (e) => {
        currentFilters.category = (document.getElementById("filter-category")?.value || "").toLowerCase();
        currentFilters.priority = (document.getElementById("filter-priority")?.value || "").toLowerCase();

        offset = 0;
        hasMore = true;
        emailList.innerHTML = "";

        filterModal.classList.add("hidden");
        loadEmails();
    })

    const sideBarLinks = document.querySelectorAll(".sidebar-link");
    sideBarLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            if (link.children[1].textContent.toLowerCase() === "inbox"){
                currentFilters.category = "";
                offset = 0;
                hasMore = true;
                emailList.innerHTML = "";
                loadEmails();
            }
            else{
                currentFilters.category = link.children[1].textContent.toLowerCase();
                offset = 0;
                hasMore = true;
                emailList.innerHTML = "";
                loadEmails();
            }
        })
    })
});