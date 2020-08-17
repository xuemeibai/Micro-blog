function refresh(){
  var past_time = new Date(Date.now());
  var last_refresh=past_time.toISOString();
  // alert('gloabl')
  if (document.getElementById("id_name_of_page").innerText==="Global Stream"){
    $.ajax({
        url: "/socialnetwork/refresh-global",
        type: "GET",
        data: "last_refresh="+last_refresh,
        dataType : "json",
        success: updateList
    });
  }else if(document.getElementById("id_name_of_page").innerText==="Follower Stream"){
    $.ajax({
        url: "/socialnetwork/refresh-follower",
        type: "GET",
        data: "last_refresh="+last_refresh,
        dataType : "json",
        success:  function(response){
          updateList(response);
        }
    });
}
}

function loadGlobalStream(){
  if (document.getElementById("id_name_of_page").innerText==="Global Stream"){
    $.ajax({
        url: "/socialnetwork/load_global",
        dataType : "json",
        success: function(response){
          updateList(response);
        }
    });
  }else if(document.getElementById("id_name_of_page").innerText==="Follower Stream"){
  
    $.ajax({
        url: "/socialnetwork/load_follower",
        dataType : "json",
        success: function(response){
          updateList(response);
        }
    });
}
}



function updateList(items){

  $(items.posts).each(function(){
    var time =new Date(this.date_created).toLocaleString("en-US");
    console.log(this);
    my_id = "id_item_post_" + this.id
    console.log(document.getElementById(my_id));

       if (document.getElementById(my_id) == null) {
         console.log('null myid')
         $("#postcontent").prepend( "<li><div id='id_item_post_"+this.id+"'>" + "Post by"+"<a href='/socialnetwork/profiles/" +
         this.user+ " 'id=id_post_profile_"+this.id+"> "  + this.first_name +this.last_name+ "</a> " +"<p>--"+
         "<span id='id_post_date_time_"+this.id+"'>"+" </span> " + time +"</span></p><br>"+
         "<span id='id_post_text_"+this.id+"'>"+" </span> " + sanitize(this.post_input_text)+"<ol id='comments_"+this.id+"'>"+"</ol>"+
         "</div>"+"Comment : <input  id='id_comment_input_text_"+ this.id +"' type='text' name='comment'>"+ "</input>"+
         "<button onclick='add_comment("+ this.id +")' id = 'id_comment_button_"+this.id+"'>Comment</button>"+"</li><br>"+"----------------------------------------------------------------------"
       )
       }
   }
 )
  $(items.comments).each(function(){
    var time =new Date(this.date_created).toLocaleString("en-US");
           my_id = "id_item_comment_" + this.id
            if (document.getElementById(my_id) == null){
          $("#comments_"+this.postid).append("<div id='id_item_comment_"+this.id+"'>"+"Comment by"+"<a href='/socialnetwork/profiles/" + this.user+
            " 'id='id_comment_profile_"+this.id+"'> " + this.first_name +this.last_name+" </a> " +
              "<p>--"+"<span id='id_comment_date_time_"+this.id+"'>"+" </span>" +time +"</span></p><br>"+ "<span id='id_comment_text_"+this.id+"'>"+
                "</span>" + sanitize(this.comment_input_text)+ "</div>"
                )}})
}



function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
}


function displayError(message) {
    $("#error").html(message);
}


function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        c = cookies[i].trim();
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length);
        }
    }
    return "unknown";
}



function add_comment(id) {
    var comment =$("#id_comment_input_text_"+id);
    var comment_text = comment.val();
    var past_time = new Date(Date.now());
    comment.val('');
    displayError('');
    $.ajax({
        url: '/socialnetwork/add-comment',
        type: "POST",
        data: "item="+comment_text+"&id="+id+ "&last_refresh="+past_time.toISOString()+"&csrfmiddlewaretoken="+getCSRFToken(),
        dataType : "json",
        success: updateList
    });
}

function add_post() {
    var post = $("#id_post_input_text");
    var post_text = post.val();
    var past_time = new Date(Date.now());
    post.val('');
    displayError('');
    $.ajax({
        url: 'socialnetwork/add_post',
        type: "POST",
        data: "item="+post_text + "&last_refresh="+past_time.toISOString()+"&csrfmiddlewaretoken="+getCSRFToken(),
        dataType : "json",
        success: updateList
    });
}


// The index.html does not load the list, so we call getList()
// as soon as page is finished loading
window.onload=loadGlobalStream;
// causes list to be re-fetched every 5 seconds
window.setInterval(refresh, 5000);
