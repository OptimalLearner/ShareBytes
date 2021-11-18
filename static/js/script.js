$(document).ready(function() {
    // Close collapsed navbar when user clicks on any nav link
    $('.navbar-nav .nav-link').on('click', function(){
        $('.navbar-collapse').collapse('hide');
    });
    // Function to highlight currently active navbar tab
    function changeActive($this) {
        $('.navbar .nav-link.active').removeClass('active');
        if (!$this.hasClass('active')) {
            $this.addClass('active');
        }
    }
    // Change active menu on nav link click
    $('.navbar .nav-link').click(changeActive($(this)));
    // Change active menu on page scroll
    $(window).scroll(function() {
        let currentWindowPos = $(this).scrollTop();
        if(currentWindowPos >= $(".company-container").offset().top-100) {
            changeActive($("#partners-link"));
        } else if(currentWindowPos >= $(".features").offset().top-100) {
            changeActive($("#features-link"));
        } else if(currentWindowPos >= $(".why-share-container").offset().top-100) {
            changeActive($("#why-share-link"));
        } else {
            changeActive($("#default-link"));
        }
    });
    // Setting up owl carousel
    $('.owl-carousel').owlCarousel({
        loop: true,
        margin: 100,
        navigation: true,
        autoplay: true,
        autoplayTimeout: 2000,
        autoplayHoverPause: true,
        responsiveClass: true,
        responsive: {
            0: {
                items: 1,
            },
            600: {
                items: 2,
            },
            1000: {
                items: 3
            }
        }
    });

    // Initially navlink for home active
    changeActive($("#default-link"));

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
        fetch('./subscribe-to-newsletter', {
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
});