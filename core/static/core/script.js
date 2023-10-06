function like(likebtn) {
    likesCountBlock = likebtn.lastElementChild;
    likesCount = likesCountBlock.innerHTML;

    if (likebtn.classList.contains('active')) {
        likebtn.classList.remove('active');
        likesCount--;
    }
    else {
        likebtn.classList.add('active');
        likesCount++;
    }

    likesCountBlock.innerHTML = likesCount;
}

function share(sharebtn) {
    sharesCountBlock = sharebtn.lastElementChild;
    sharesCount = sharesCountBlock.innerHTML;

    if (sharebtn.classList.contains('active')) {
        sharebtn.classList.remove('active');
        sharesCount--;
    }
    else {
        sharebtn.classList.add('active');
        sharesCount++;
    }

    sharesCountBlock.innerHTML = sharesCount;
}

function favouriteMovie() {
    const btn = document.getElementById('favouriteBtn');

    if (btn.classList.contains('active')) {
        btn.classList.remove('active');
    }
    else {
        btn.classList.add('active');
    }

}

function followBtn(btn) {
    if (btn.classList.contains('active')) {
        btn.classList.remove('active');
        btn.innerHTML = 'Follow';
    }
    else {
        btn.classList.add('active');
        btn.innerHTML = 'Following';
    }
}


function showCast(btn) {
    const hiddenCast = document.getElementById('hidden-cast');
    const allCast = document.getElementById('casts');

    if (hiddenCast.style.display == 'none') {
        hiddenCast.style.display = 'flex';
        btn.innerHTML = '&times;';
    }
    else {
        hiddenCast.style.display = "none";
        btn.innerHTML = 'See More...';
    }

    window.onclick = function (event) {
        if (event.target == allCast) {
            hiddenCast.style.display = "none";
            btn.style.display = 'flex';
        }
    }
}

function closeMessage(btn) {
    message = btn.parentElement;
    message.remove();
}