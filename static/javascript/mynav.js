    /* Set the width of the side navigation to 250px */
/** ANIMATED 
function openNav() {
document.getElementById("mySidenav").style.width = "250px";
}

function closeNav() {
document.getElementById("mySidenav").style.width = "0";
} 

FIXED
function openNav() {
document.getElementById("mySidenav").style.display = "block";
}


function closeNav() {
document.getElementById("mySidenav").style.display = "none";
} 
**/
/** PUSH CONTENT **/
function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
    }
    
    function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("main").style.marginLeft= "0";
    }
    