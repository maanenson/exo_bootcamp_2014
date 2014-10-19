function(container, portal) {
  var html = '';
  var dataport_name = '';


  function refreshDeviceList()
  {
    var xmlHttp = null;

    var portal_id = window.location.pathname.split('/')[2];

    // GET A LIST OF DEVICES OWNED BY THIS PORTAL
    xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", '/api/portals/v1/portals/'+portal_id, true );
    xmlHttp.setRequestHeader( 'Content-Type', 'application/json' );

    xmlHttp.onload = function (e) {
      if (xmlHttp.readyState === 4) {
        if (xmlHttp.status === 200) {
          //console.log(xmlHttp.responseText);
          
          var json_response = xmlHttp.responseText;

          var portal_resources = JSON.parse(json_response, function (key, value) 
          {
            var type;
            if (value && typeof value === 'object') {
                type = value.type;
                if (typeof type === 'string' && typeof window[type] === 'function') {
                    return new (window[type])(value);
                }
            }
            return value;
          });
          console.log(portal_resources);

          //Update the device list
          var html_device_table = "";
          for (var i = 0; i<portal_resources['devices'].length; i++)
          {
            html_device_table +=  '<div>'+String(i+1) + '.  '+ String(portal_resources['devices'][i]) +'</div>';
          }
          $(container).find('div#list').html(html_device_table);

        } else { console.error(xmlHttp.statusText); }
      }
    };
    xmlHttp.onerror = function (e) {
      console.error(xmlHttp.statusText);
    };
    xmlHttp.send( null );
  }


  html = '<div style="padding:20px 20px">';
  html += '<h2>Device List</h2>';
  html += '<div id="list" style="font-size:100%;line-height:1.0em;">loading...</div>';
  html += '</div>';
  
  $(container).html(html);

  refreshDeviceList();

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

