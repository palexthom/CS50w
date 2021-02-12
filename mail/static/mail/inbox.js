document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email());

 // Add event listener for the submit of the send form
  document.querySelector('#compose-form').addEventListener('submit', () => send_email());

  // Add listener for the reply button
  document.querySelector('#reply-button').addEventListener('click', () => compose_reply());

  // Add listeners to the archive and unarchive buttons
   document.querySelector('#archive').addEventListener('click', () => {
            console.log("Button archive clicked once --› archive!");
            archive(true);
            });

   document.querySelector('#unarchive').addEventListener('click', () => {
            console.log("Button unarchive clicked once --› unarchive!");
            archive(false);
            });

  // By default, load the inbox
  load_mailbox('inbox');

});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

    console.log("Compose_email : done")
}


function compose_reply() {
    console.log("Compose_reply : done")
   // try to
    var email_from = document.querySelector('#email-from').innerHTML
    console.log(email_from)

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = document.querySelector('#email-from').innerHTML;
  document.querySelector('#compose-subject').value = "RE: " + document.querySelector('#email-subject').innerHTML;
  document.querySelector('#compose-body').value = '';

    // Show compose view and hide other views
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'none';

  // Fill in the user we're replying to
    console.log("Compose_email : done")
}


function add_email(contents) {
    // Create new email in a div
    const email = document.createElement('div');

    if (contents.read) {
        email.className = 'border border-dark rounded p-2 m-2 bg-white';
        email
    } else {
        email.className = 'border border-dark rounded p-2 m-2 bg-light font-weight-bold';
    }
    email.id = `${contents.id}`
    email.innerHTML = `<div class="email"> ${contents.timestamp} — From: ${contents.sender} — Subject: ${contents.subject} </div> `;

    // Add an EventListener
    email.addEventListener('click', function() {
        // Show/Hide what has to
        document.querySelector('#emails-view').style.display = 'none';
        document.querySelector('#single-email-view').style.display = 'block';
        document.querySelector('#compose-view').style.display = 'none';
        // Load email
        load_email(email.id);
        // Mark email as read
        mark_read(email.id);
    });

    // Add post to DOM
    document.querySelector('#emails-view').append(email);
};


function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#single-email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  // Show unread messages if mailbox is inbox (I know this could be better with React)
  if (mailbox === 'inbox'){
    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)} <span id="unread"></span></h3>`;
  }
  else {
    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  }

  // Query the mails from that box
  console.log("Let's fetch mails from box: ", `/emails/${mailbox}`)
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
      // Print emails
      console.log(emails);
      if (mailbox === 'inbox'){
        count_unread(emails)
      }
      emails.forEach(add_email);
    });
}


function send_email() {
     fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          recipients: document.getElementById("compose-recipients").value,
          subject: document.getElementById("compose-subject").value,
          body: document.getElementById("compose-body").value
      })
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log(result);
    })
    .then(result => {
        load_mailbox('sent');
    });
}


function load_email(email_id) {
    console.log("Loading email", email_id);
    fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
        // Print email
        console.log(email);
        console.log(email.subject);

        // Update div content to show email
        document.getElementById("single-email").innerHTML = `<div class="my-2"><u>Date</u> : ${email.timestamp}</div>
                                <div class="my-2"><u>From</u> : <span id="email-from">${email.sender}</span></div>
                                <div class="my-2"><u>To</u> : <span id="email-to">${email.recipients}</span></div>
                                <div class="my-2"><u>Subject</u> : <span id="email-subject">${email.subject}</span></div>
                                <div id="email-body my-2">${email.body}</div>
                                <div id="email-id" style="display: none;">${email.id}</div>`


        // Show archive or unarchive button depending on status
        console.log("load_email : archived ?", email.archived)
        if (email.archived) {

        }
        else {
            document.querySelector('#archive').style.display = 'block';
            document.querySelector('#unarchive').style.display = 'none';
        }

        // Show reply and (un)archive buttons depending on status (can't reply to own email)
        if (email.sender === document.getElementById("user-email").innerHTML) {
            // if user is author of an email, it is "sent" and cannot be replied or archived
            document.querySelector('#reply-button').style.display = 'none';
            document.querySelector('#archive').style.display = 'none';
            document.querySelector('#unarchive').style.display = 'none';
        }
        else {
            // if user isn't sender, we show the reply button
            document.querySelector('#reply-button').style.display = 'block';

            if (email.archived) {
                // if email is archived, we show unarchive
                document.querySelector('#unarchive').style.display = 'block';
                document.querySelector('#archive').style.display = 'none';
            }
            else {
                // else we show archived
                document.querySelector('#archive').style.display = 'block';
                document.querySelector('#unarchive').style.display = 'none';
            }
        }

        console.log("Done with load_email")
});
}

function mark_read(email_id){
    console.log("Lets mark as read")
    console.log(`/emails/${email_id}`)
    fetch(`/emails/${email_id}`, {
      method: 'PUT',
      body: JSON.stringify({
          read: true
      })
})
}

function archive(archive){
    // change archive status
    console.log("Lets's archive or unarchive")
    console.log(archive)
    console.log(document.getElementById('email-id').innerHTML)

    const email_id = document.getElementById('email-id').innerHTML
    // change status of the email
    fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: archive
        })
    })
    .then(() => {
        console.log("Done with changing archive status");})
    .then(() => {
        console.log("Let's load the inbox");
        load_mailbox("inbox");
    });
}

function count_unread(emails){
    console.log("entering count_unread");
    var i;
    var count = 0;
    console.log(emails.length);
    for (i = 0; i < emails.length; i++) {
        console.log(emails[i].read)
        if (!emails[i].read) {
          count+=1;
        }
    }

    if (count != 0) {
        document.getElementById("unread").innerHTML=`(${count} unread)`;
    }
    else {
        document.getElementById("unread").innerHTML=``;
    };
}