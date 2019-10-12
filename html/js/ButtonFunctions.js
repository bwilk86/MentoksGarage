function GarageDoor(act){
    var apiUrl="http://10.199.248.169:8090/api/door";
    var data={action: act};
    $.ajax({
    url: apiUrl,
    type: 'POST',
    dataType: 'json',
    data: data,
    success: function(d){
    alert("This worked");},
    error: function(){alert("This didn't work");}
    });
}