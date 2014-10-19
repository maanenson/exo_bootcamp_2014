function(container, portal) {
  var html = '';
  var dataport_name = '';

  var devices_list = [];

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
          for (var i = 0; i<portal_resources['devices'].length; i++)
          {
            devices_list.push(portal_resources['devices'][i]);
          }

          refreshDeviceInformation();

        } else { console.error(xmlHttp.statusText); }
      }
    };
    xmlHttp.onerror = function (e) {
      console.error(xmlHttp.statusText);
    };
    xmlHttp.send( null );
  }


  function refreshDeviceInformation()
  {
    
    var html_device_table = '<table cellpadding="5" width="100%"><tr><th>#</th><th>RID</th><th>Name</th><th>Type</th><th>Status</th></tr>';

    // GET A LIST OF DEVICES OWNED BY THIS PORTAL
    for (var i = 0; i < devices_list.length; i++)
    {
      var xmlHttp = null;
      xmlHttp = new XMLHttpRequest();
      xmlHttp.open( "GET", '/api/portals/v1/devices/' + devices_list[i] + '', false ); //false -> NOTE THIS IS SYNCHRONOUS
      xmlHttp.setRequestHeader( 'Content-Type', 'application/json' );

      xmlHttp.onload = function (e) {
        if (xmlHttp.readyState === 4) {
          if (xmlHttp.status === 200) {
            //console.log(xmlHttp.responseText);
            
            var json_response = xmlHttp.responseText;

            var device_resources = JSON.parse(json_response, function (key, value) 
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
            console.log(device_resources);

            var prov_status = 'unknown',
                dev_name = 'unknown',
                dev_vendor = '',
                dev_model = 'custom',
                dev_sn = '';

            if (device_resources['info']['basic']['status']) 
            {
              prov_status = device_resources['info']['basic']['status'];
              if (prov_status == 'notactivated') { prov_status = 'Not Activated'; }
              if (prov_status == 'activated') { prov_status = 'Activated'; }
            }
            if ( device_resources['info']['description']['name']) { dev_name = device_resources['info']['description']['name']; }
            if(device_resources['type']=='vendor') 
            { dev_vendor = device_resources['vendor']; 
              dev_model = device_resources['model']; }
            else 
            {(dev_model = 'generic');}
            if(device_resources['sn']){ dev_sn = device_resources['sn'];}

            //UPDATE HTML DEVICE LIST STRING
            html_device_table += '<tr>';
            html_device_table += '<td>'+ String(i+1) + '</td>';
            html_device_table += '<td>'+ String(devices_list[i])+ '</td>'; //RID
            html_device_table += '<td>'+ dev_name+ '</td>';
            html_device_table += '<td>'+ dev_model+ '</td>';
            html_device_table += '<td>'+ prov_status+ '</td>'; 
            html_device_table += '</tr>';
            html
            

          } else { console.error(xmlHttp.statusText); }
        }
      };
      xmlHttp.onerror = function (e) {
        console.error(xmlHttp.statusText);
      };
      xmlHttp.send( null );
    }
    html_device_table += '</table>';
    //ACTUALLY UPDATE THE HTML DEVICE LIST
    $(container).find('div#list').html(html_device_table);

  }


  html = '<div style="padding:20px 20px">';
  html += '<h2>Device List</h2>';
  html += '<div id="list" style="font-size:100%;line-height:1.0em;">loading...</div>';
  html += '</div>';
  
  $(container).html(html);

  refreshDeviceList();

  
}

