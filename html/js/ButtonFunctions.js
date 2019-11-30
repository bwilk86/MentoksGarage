function GarageDoor(act){
    if(act == "open"){
        $('#garageDoorOpen').addClass('disabled');
        $('#garageDoorOpen').attr('disabled', 'disabled');
        $('#garageDoorClose').removeClass('disabled');
        $('#garageDoorClose').removeAttr('disabled', 'disabled');
    }
    else{
        $('#garageDoorClose').addClass('disabled');
        $('#garageDoorClose').attr('disabled', 'disabled');
        $('#garageDoorOpen').removeClass('disabled');
        $('#garageDoorOpen').removeAttr('disabled');
        }
    // var apiUrl="http://10.199.248.169:8090/api/garagedoor/";
    // var data={performprocess: act};
    // $.post(apiUrl,data,function(response){alert(response.status)});
	
	$.ajax({
		type: 'GET',
		url: 'https://localhost:44354/api/Values/1',
		dataType: 'json',
		success: function(data){
			alert(data.status);
		}
	});
}
function GarageLights(act){
    if(act == "on"){
        $('#garageLightsOn').addClass('disabled');
        $('#garageLightsOn').attr('disabled', 'disabled');
        $('#garageLightsOff').removeClass('disabled');
        $('#garageLightsOff').removeAttr('disabled', 'disabled');
    }
    else{
        $('#garageLightsOff').addClass('disabled');
        $('#garageLightsOff').attr('disabled', 'disabled');
        $('#garageLightsOn').removeClass('disabled');
        $('#garageLightsOn').removeAttr('disabled');
        }
    var apiUrl="http://10.199.248.169:8090/api/lights/";
    var data={performprocess: act};
    $.post(apiUrl,data,function(response){alert(response.status)});
}