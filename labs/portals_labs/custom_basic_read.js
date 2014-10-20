function(container, portal) {
  var html = '';
  var dataport_name = '';

  console.log(portal);
  if (portal.clients.length == 0){
    html = '<div style="padding:20px 20px">';
    html += '<h2>Please select a Client Data from Widget Options</h2>';
    html += '</div>';
    $(container).html(html);
    return;
  }

  dataport_name = portal.clients[0].dataports[0].info.description.name;

  function reload() {
    // call the read widget API
    var options = {
      starttime: 1,                          // beginning of epoch
      //endtime: (new Date).getTime() / 1000,  // default is 'now'
      limit: 1,                              // single point
      sort: "desc"                           // latest point
    };

    //Note: This will only read for the first dataport for the first client passed in
    //by the portal array resource passed into the widget container function
    //
    read([portal.clients[0].alias, portal.clients[0].dataports[0].alias], options)
      .done(function() {
        var data = arguments;
        // update the data.
        var latest_point = data[0];
        var html = latest_point[1];
        $(container).find('div#temperature').html(html);
        $(container).find('div#time').html('' + new Date(latest_point[0] * 1000)  + '')
        $(container).find('div#status').html(' ');
      })
      .fail(function() {
        $(container).find('span#temperature').html(data);
        $(container).find('div#status').html('there was an error');
      });
  }

  html = '<div style="padding:20px 20px">';
  html += '<h2>Latest '+dataport_name+ ' Value:</h2>';
  html += '<div id="temperature" style="font-size:48px; height:1.5em;line-height:1.5em;"> </div>';
  html += '<div id="time" style="font-size:smaller"> </div>';
  html += '<div id="status" style="font-size:small;padding:2px 0px;height:1.5em">loading...</div>';
  html += '<div><a class="reload" href="javascript:void(0);">manual reload</a></div>';
  html += '</div>';
  
  $(container).html(html);

  $(container).find('a.reload').click(function() {
    // read value again when user clicks on "reload" link
    console.log("re-loading value");
    reload();
  });

  // read value when widget loads
  reload(); //COMMENT THIS OUT IF USING SELF REFRESH CODE BELOW

  /*
  // AUTO RELOAD - SELF REFRESH
  var counter = 30; //only refresh 30 times before quiting
  function autoreload(){
    counter--;
    console.log(counter);
    $(container).find('div#status').html('refreshing...');
    if(counter>0){
      reload();
      setTimeout(autoreload,2000);
    }
    else{
      $(container).find('div#status').html('auto refresh stopped');
    }
  }
  autoreload();
  */
  
}

