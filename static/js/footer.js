document.querySelector(".newsletter-btn").addEventListener("click", () => {
    let emailForNewsletter = document.querySelector(".newsletter-email").value;
    if(emailForNewsletter== '') {
        alert('No value entered');
        return;
    }
    // Email Validation
    if(!validateEmail(emailForNewsletter)) {
        return;
    }
    fetch(domain + newsletterUrl, {
        method: "POST",
        headers : { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({newsletterEmail: emailForNewsletter})
    })
    .then(
        res => res.json()
    ).then(
        res => alert(res['message'])
    ).catch(
        err => console.log("Error: " + err)
    );
    document.querySelector(".newsletter-email").value = '';
});

function validateEmail(email) {
    var validRegex = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    if (email.match(validRegex)) {
        return true;
    } else {
        alert("Invalid email address!");      
        return false;
    }
}