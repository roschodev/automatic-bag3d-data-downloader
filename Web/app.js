document.addEventListener('DOMContentLoaded', function() {
    //Map Initialization Data
        //Set Maximum bounds on map
    var netherlandsBounds = [[50.5, 3.2], [53.6, 7.2]];

        // Define Map Rules
    var map = L.map('map', {
        center: [52.1, 5.3],
        zoom: 8,
        maxBounds: netherlandsBounds,
        maxBoundsViscosity: 1.0,
        minZoom: 8,
        maxZoom: 18
      }); 

        // Define the map layer to be used
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
  
    
    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);
  
    var drawControl = new L.Control.Draw({
      edit: {
        featureGroup: drawnItems,
        edit: true,
        remove: true
      },
      draw: {
        rectangle: false,
        polygon: false,
        circle: false,
        marker: false,
        polyline: false,
        circlemarker: false
      }
    });
    map.addControl(drawControl);
  
    var rectangle;

    var projectname;

    addRectangleButton = document.getElementById("add");
    confirmProjectButton = document.getElementById("confirm");
  
    window.addRectangle = function(size) {
      let bounds;
      const center = map.getCenter();
  
      switch(size) {
        case 'small':
          bounds = [
            [center.lat - 0.01, center.lng - 0.01],
            [center.lat + 0.01, center.lng + 0.01]
          ];
          break;
        case 'medium':
          bounds = [
            [center.lat - 0.1, center.lng - 0.2],
            [center.lat + 0.1, center.lng + 0.2]
          ];
          break;
        case 'large':
          bounds = [
            [center.lat - 0.2, center.lng - 0.4],
            [center.lat + 0.2, center.lng + 0.4]
          ];
          break;
        default:
          return;
      }
  
      if (rectangle) {
        drawnItems.removeLayer(rectangle);
      }
  
      rectangle = L.rectangle(bounds, {color: "#ff7800", weight: 1}).addTo(drawnItems);
      map.fitBounds(bounds);
      
      addRectangleButton.classList.add('hidden');
      confirmProjectButton.classList.remove('hidden')
      //document.querySelectorAll('#controls button:not(#confirm)').forEach(button => button.style.display = 'none');
      //document.getElementById('confirm').style.display = 'inline-block';
    }
  
    window.confirmRectangle = function() {
      if (!rectangle) return;
  
      var bounds = rectangle.getBounds();
      var nw = bounds.getNorthWest();
      var se = bounds.getSouthEast();
  
      var epsg28992 = "+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.2369,50.0087,465.658,0.406857330322142,0.350732676542563,1.8703473836068,4.0812 +units=m +no_defs";
      var nwCoord = proj4('EPSG:4326', epsg28992, [nw.lng, nw.lat]);
      var seCoord = proj4('EPSG:4326', epsg28992, [se.lng, se.lat]);

      console.log("NW Coordinate: ", nwCoord);
      console.log("SE Coordinate: ", seCoord);

      // const coordtext = document.querySelector("#coordinateText");
      // coordtext.innerHTML = `NW Coordinate: ${nwCoord} -- SE Coordinate: ${seCoord}`;
  
      sendCoordsToServer(nwCoord, seCoord);
  
      //document.querySelectorAll('#controls button:not(#confirm)').forEach(button => button.style.display = 'inline-block');
      //document.getElementById('confirm').style.display = 'none';
      drawnItems.removeLayer(rectangle);
      rectangle = null;

      var inputProjectName = document.getElementById('projectname-input').value;
      projectname = inputProjectName.value;
    }
    
    // Function to send coordinates to the server
    function sendCoordsToServer(nwCoord, seCoord) {
      fetch('http://127.0.0.1:5500/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          nw_coord: nwCoord,
          se_coord: seCoord,
          project_name: projectname
        })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text().then(text => text ? JSON.parse(text) : {});
      })
      .then(data => {
        if (data.errors) {
          console.error('Errors:', data.errors);
        } else {
          console.log('Output:', data.output);
        }
      })
      .catch(error => {
        const statusText = document.querySelector("#statusText");
        statusText.innerHTML = error;
      })
  }
});
 