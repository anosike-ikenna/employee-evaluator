$(function() {
    var message = document.body.querySelector(".dj-message");
    if(message) {
        for (let x of message.children) {
            x.style.listStyle = "none";
        }
        setTimeout(() => message.remove(), 3000);
    };
    // var req = $.ajax({
    //     "url": "/api/designations/",
    //     "type": "get",
    //     "dataType": "json",
    // });

    // req.done(function(results, status, jqXHR) {
    //     console.log(status);
    //     console.log(jqXHR);
    //     console.log(results);
    // })

    // req.fail(function(jqXHR, status, errorThrown){
    //     console.log(jqXHR);
    //     console.log(status);
    //     console.log(errorThrown);
    // })
});