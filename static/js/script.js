let mobileMenuIcon = document.getElementById("mobile-menu-icon");
let mobileMenuDiv = document.querySelector(".sidebar-menu");
let closeMenuBtn = document.querySelector(".close-menu-btn");
let categoryItems = document.querySelectorAll(".category-items");
let sidebar = document.querySelector(".sidebar-menu");
let toggleBtn = document.getElementById("toggle-btn");
let categoryContainer = document.querySelector(".category-section");
let leftNavBtn = document.getElementById("left-nav-btn");
let rightNavBtn = document.getElementById("right-nav-btn");
const scrollAmount = categoryItems[0].offsetWidth + 20;

leftNavBtn.addEventListener("click", () => {
    categoryContainer.scrollBy({left: -2 * scrollAmount, behavior: "smooth"});
});

rightNavBtn.addEventListener("click", () => {
    categoryContainer.scrollBy({left: 2 * scrollAmount, behavior: "smooth"});
});

function toggleSubmenu(button){

    if(!button.nextElementSibling.classList.contains("show")){
        closeAllSubmenus();
    }

    button.nextElementSibling.classList.toggle("show");
    button.classList.toggle("rotate");

    if(sidebar.classList.contains("hide")){
        sidebar.classList.toggle("hide");
        toggleBtn.classList.toggle("rotate");
    }

}

function toggleSidebar(){
    sidebar.classList.toggle("hide");
    toggleBtn.classList.toggle("rotate");

    closeAllSubmenus();
}

function closeAllSubmenus(){
    Array.from(sidebar.getElementsByClassName("show")).forEach(menu => {
        menu.classList.remove("show");
        menu.previousElementSibling.classList.remove("rotate");
    })
}

categoryItems.forEach(item => {
    const shadow = item.querySelector(".scrollable-shadow-box");
    const updateShadow = () => {
        const isAtBottom = item.scrollTop + item.clientHeight >= item.scrollHeight;
        const isAtTop  = item.scrollTop === 0;
        
        if (isAtTop && !isAtBottom){
            shadow.style.opacity = "1";
        }
        else{
            shadow.style.opacity = "0";
        } 
    }

    if (item.scrollHeight > item.clientHeight) {
        shadow.style.opacity = '1';
    }


    item.addEventListener("scroll", updateShadow);
    window.addEventListener("resize", updateShadow);

});