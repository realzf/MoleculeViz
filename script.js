$(document).ready(function() {
  
  $('a[href="#addElement"]').click(function() {
    $('#addElement').show();
    $('#uploadSDF').hide();
    $('#removeElement').hide();
    $('#displayMolecule').hide();
    $('#svgContainer').hide();
  });

  $('a[href="#uploadSDF"]').click(function() {
    $('#addElement').hide();
    $('#uploadSDF').show();
    $('#removeElement').hide();
    $('#displayMolecule').hide();
    $('#svgContainer').hide();
  });

  $('a[href="#removeElement"]').click(function() {
    $('#addElement').hide();
    $('#uploadSDF').hide();
    $('#removeElement').show();
    $('#displayMolecule').hide();
    $('#svgContainer').hide();
  });

  $('a[href="#displayMolecule"]').click(function() {
    $('#displayMolecule').show();
    $('#uploadSDF').hide();
    $('#removeElement').hide();
    $('#addElement').hide();
    $('#svgContainer').show();
  });

  $('#uploadSDF form').submit(function(e) {
    e.preventDefault(); 
    var formData = new FormData();
    formData.append('file', $('#file').prop('files')[0]);
    formData.append('molecule_name', $('#molecule_name').val());
  
    $.post({
      url: 'sdf',
      data: formData,
      processData: false,
      contentType: false,
      success: function(data, status) {
        alert(data.message);
        $('#uploadSDF form')[0].reset();
        location.reload()
      },
      error: function(xhr, status, error) {
        alert('Error!');
      }
    });
  });

  $('#addElementForm').submit(function(event) {
    event.preventDefault(); 

    var formData = {
      element_number: $('#elementNumber').val(),
      element_code: $('#elementCode').val(),
      element_name: $('#elementName').val(),
      color1: $('#color1').val(),
      color2: $('#color2').val(),
      color3: $('#color3').val(),
      radius: $('#radius').val()
    };

    $.ajax({
      type: 'POST',
      url: 'addElement',
      data: formData,
      
      success: function(data, status) {
        alert(data.message);
        $('#addElementForm')[0].reset();

        $.ajax({
          url: '/removeElement',
          type: 'GET',
          dataType: 'json',
          success: function(data) {
            $('#elementTable tbody').empty();
            $.each(data, function(index, element) {
              var tr = $('<tr>');
              tr.append($('<th scope="row">').text(element[0]));
              tr.append($('<td>').text(element[1]));
              tr.append($('<td>').text(element[2]));
              tr.append($('<td>').html(`<button type="submit" id=${element[1]} class="btn btn-danger">Delete</button>`));
              $('#elementTable tbody').append(tr);
            });
          }
        });
      },
      error: function(xhr, status, error) {
        alert('Error!');
      }
    });
  });

  $.ajax({
    url: '/removeElement',
    type: 'GET',
    dataType: 'json',
    success: function(data) {
      $.each(data, function(index, element) {
        var tr = $('<tr>');
        tr.append($('<th scope="row">').text(element[0]));
        tr.append($('<td>').text(element[1]));
        tr.append($('<td>').text(element[2]));

        tr.append($('<td>').html(`<button type="submit" id=${element[1]} class="btn btn-danger">Delete</button>`));
        $('#elementTable tbody').append(tr);
      });
    }
  });

  $('#removeElementForm').submit(function(event) {
    event.preventDefault();
    var clickedButtonId = event.originalEvent.submitter.id;
    
    $.ajax({
      url: '/deleteElement',
      type: 'POST',
      data: { element_code: clickedButtonId },
      success: function(response) {
        $.ajax({
          url: '/removeElement',
          type: 'GET',
          dataType: 'json',
          success: function(data) {
            $('#elementTable tbody').empty();
            $.each(data, function(index, element) {
              var tr = $('<tr>');
              tr.append($('<th scope="row">').text(element[0]));
              tr.append($('<td>').text(element[1]));
              tr.append($('<td>').text(element[2]));
              tr.append($('<td>').html(`<button type="submit" id=${element[1]} class="btn btn-danger">Delete</button>`));
              $('#elementTable tbody').append(tr);
            });
          }
        });
      },
    });
  });

  $.ajax({
    url: '/displayMolecule',
    type: 'GET',
    dataType: 'json',
    success: function(data) {
      $.each(data, function(index, element) {
        var tr = $('<tr>');
        tr.append($('<th scope="row">').text(element[1]));
        tr.append($('<td>').html(`<button type="submit" id=${element[1]} class="btn btn-primary">Select</button>`));
        $('#moleculeTable tbody').append(tr);
      });
    }
  });

  $('#displayMoleculeForm').submit(function(event) {
    event.preventDefault();
    var clickedButtonId = event.originalEvent.submitter.id;
    
    $.ajax({
      url: '/svg',
      type: 'POST',
      data: { molecule_name: clickedButtonId },
      success: function(response) {
        var svgData = response 
        var serializer = new XMLSerializer()
        var svgString = serializer.serializeToString(svgData)
        $('#svgContainer').html('<h2 style="text-decoration:none;">' + clickedButtonId + ' Molecule:</h2>' + svgString);
      },
    });
  });
});