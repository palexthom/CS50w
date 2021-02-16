document.addEventListener('DOMContentLoaded', function() {

    // show compose view on click
    document.querySelector('#post-link').addEventListener('click', () => show_compose_post());

    // submit new post
    document.querySelector('#post-submit').addEventListener('click', () => send_post());

    // By default, hide compose post
    hide_compose_post()

    // If page is user/xxx then show div with user info
    if (location.href.indexOf("/user/") != -1){
        document.querySelector('#user-info').style.display = 'block';
        follow_button()
    }
    else {
        document.querySelector('#user-info').style.display = 'none';
    }

});

function show_compose_post() {
    // Show compose view
    document.querySelector('#compose-view').style.display = 'block';
    // Clear out composition
    document.querySelector('#post-body').value = '';
}

function hide_compose_post() {
    // Show compose view
    document.querySelector('#compose-view').style.display = 'none';
}

function send_post(){
    console.log("Sending post");
       fetch('/posts/compose', {
        method: 'POST',
        body: JSON.stringify({
            body: document.getElementById("post-body").value
        })
      })
      .then(response => response.json())
      .then(result => {
        // Print result
        console.log(result);
      })
      .then(
        location.reload()
      )
}


function add_post(contents) {
    // creates a new post in a div
    const post = document.createElement('div');
    post.id = `${contents.id}`
    post.className = 'border border-dark rounded p-2 m-2 bg-white';
    post.innerHTML = `<div class="post"> <div>${contents.body}</div><div>${contents.timestamp} — <a href="#" onclick="load_feed(Pierre);return false"; >${contents.author}</a></div></div> `;
    document.querySelector('#feed').append(post);
}

function follow_button() {
    console.log("Let's investigate about what we know already about the user");
    console.log(document.getElementById("profile-name").value)
    if (document.getElementById("username").value == document.getElementById("profile-name").value) {
        // if it's me don't display any button
        document.querySelector('#follow').style.display = 'none';
        document.querySelector('#unfollow').style.display = 'none';
    }
    else if (document.getElementById("is-following").value == 'True') {
        // if i'm following, show unfollow
        document.querySelector('#follow').style.display = 'none';
        document.querySelector('#unfollow').style.display = 'block';
    }
    else {
        // if I'm not following, show follow
        document.querySelector('#follow').style.display = 'block';
        document.querySelector('#unfollow').style.display = 'none';
    }
}


function follow(){
    console.log("Click on follow")
    console.log(document.querySelector("#url-follow").dataset.url)
    window.location.replace(document.querySelector("#url-follow").dataset.url);
}

function unfollow(){
    console.log("Click on unfollow")
    console.log(document.querySelector("#url-unfollow").dataset.url)
    window.location.replace(document.querySelector("#url-unfollow").dataset.url);

}




