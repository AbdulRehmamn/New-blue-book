//hmapsprem - frontend map management

//plugin globals
var hmapsprem_map_loaded = false;
var hmapsprem_loading_gmaps = false;
var hmapsprem_info_window_pointer = [];
var hmapsprem_markers_object;
var hmapsprem_markers_object_available = false;
var map_themes = {
	"Default": "",
	"Subtle Grayscale": [{"featureType":"landscape","stylers":[{"saturation":-100},{"lightness":65},{"visibility":"on"}]},{"featureType":"poi","stylers":[{"saturation":-100},{"lightness":51},{"visibility":"simplified"}]},{"featureType":"road.highway","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"road.arterial","stylers":[{"saturation":-100},{"lightness":30},{"visibility":"on"}]},{"featureType":"road.local","stylers":[{"saturation":-100},{"lightness":40},{"visibility":"on"}]},{"featureType":"transit","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"administrative.province","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":-25},{"saturation":-100}]},{"featureType":"water","elementType":"geometry","stylers":[{"hue":"#ffff00"},{"lightness":-25},{"saturation":-97}]}],
	"Unsaturated Browns": [{"elementType":"geometry","stylers":[{"hue":"#ff4400"},{"saturation":-68},{"lightness":-4},{"gamma":0.72}]},{"featureType":"road","elementType":"labels.icon"},{"featureType":"landscape.man_made","elementType":"geometry","stylers":[{"hue":"#0077ff"},{"gamma":3.1}]},{"featureType":"water","stylers":[{"hue":"#00ccff"},{"gamma":0.44},{"saturation":-33}]},{"featureType":"poi.park","stylers":[{"hue":"#44ff00"},{"saturation":-23}]},{"featureType":"water","elementType":"labels.text.fill","stylers":[{"hue":"#007fff"},{"gamma":0.77},{"saturation":65},{"lightness":99}]},{"featureType":"water","elementType":"labels.text.stroke","stylers":[{"gamma":0.11},{"weight":5.6},{"saturation":99},{"hue":"#0091ff"},{"lightness":-86}]},{"featureType":"transit.line","elementType":"geometry","stylers":[{"lightness":-48},{"hue":"#ff5e00"},{"gamma":1.2},{"saturation":-23}]},{"featureType":"transit","elementType":"labels.text.stroke","stylers":[{"saturation":-64},{"hue":"#ff9100"},{"lightness":16},{"gamma":0.47},{"weight":2.7}]}],
	"Rich Black": [{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#222222"},{"visibility":"on"}]}],
	"Blue water": [{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#46bcec"},{"visibility":"on"}]}],
	"Pale Dawn": [{"featureType":"administrative","elementType":"all","stylers":[{"visibility":"on"},{"lightness":33}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2e5d4"}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#c5dac6"}]},{"featureType":"poi.park","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":20}]},{"featureType":"road","elementType":"all","stylers":[{"lightness":20}]},{"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#c5c6c6"}]},{"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#e4d7c6"}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#fbfaf7"}]},{"featureType":"water","elementType":"all","stylers":[{"visibility":"on"},{"color":"#acbcc9"}]}],
	"Cobalt": [{"featureType":"all","elementType":"all","stylers":[{"invert_lightness":true},{"saturation":10},{"lightness":30},{"gamma":0.5},{"hue":"#00aaff"}]},{"featureType":"administrative.province","elementType":"geometry.stroke","stylers":[{"saturation":"100"},{"lightness":"27"}]},{"featureType":"landscape","elementType":"geometry.fill","stylers":[{"color":"#32373c"}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"saturation":"100"},{"lightness":"69"},{"gamma":"1.40"}]},{"featureType":"road.highway","elementType":"labels.text.fill","stylers":[{"lightness":"100"},{"saturation":"100"}]},{"featureType":"road.highway.controlled_access","elementType":"labels.icon","stylers":[{"saturation":"100"}]},{"featureType":"road.arterial","elementType":"geometry.fill","stylers":[{"saturation":"43"},{"lightness":"51"}]},{"featureType":"road.arterial","elementType":"labels.text.fill","stylers":[{"saturation":"45"},{"lightness":"19"}]}],
	"Retro": [{"featureType":"administrative","stylers":[{"visibility":"off"}]},{"featureType":"poi","stylers":[{"visibility":"simplified"}]},{"featureType":"road","elementType":"labels","stylers":[{"visibility":"simplified"}]},{"featureType":"water","stylers":[{"visibility":"simplified"}]},{"featureType":"transit","stylers":[{"visibility":"simplified"}]},{"featureType":"landscape","stylers":[{"visibility":"simplified"}]},{"featureType":"road.highway","stylers":[{"visibility":"off"}]},{"featureType":"road.local","stylers":[{"visibility":"on"}]},{"featureType":"road.highway","elementType":"geometry","stylers":[{"visibility":"on"}]},{"featureType":"water","stylers":[{"color":"#84afa3"},{"lightness":52}]},{"stylers":[{"saturation":-17},{"gamma":0.36}]},{"featureType":"transit.line","elementType":"geometry","stylers":[{"color":"#3f518c"}]}],
	"Red Alert": [{"featureType":"all","elementType":"all","stylers":[{"visibility":"simplified"},{"saturation":"-100"},{"invert_lightness":true},{"lightness":"11"},{"gamma":"1.27"}]},{"featureType":"administrative.locality","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"landscape.man_made","elementType":"all","stylers":[{"hue":"#ff0000"},{"visibility":"simplified"},{"invert_lightness":true},{"lightness":"-10"},{"gamma":"0.54"},{"saturation":"45"}]},{"featureType":"poi.business","elementType":"all","stylers":[{"visibility":"simplified"},{"hue":"#ff0000"},{"saturation":"75"},{"lightness":"24"},{"gamma":"0.70"},{"invert_lightness":true}]},{"featureType":"poi.government","elementType":"all","stylers":[{"hue":"#ff0000"},{"visibility":"simplified"},{"invert_lightness":true},{"lightness":"-24"},{"gamma":"0.59"},{"saturation":"59"}]},{"featureType":"poi.medical","elementType":"all","stylers":[{"visibility":"simplified"},{"invert_lightness":true},{"hue":"#ff0000"},{"saturation":"73"},{"lightness":"-24"},{"gamma":"0.59"}]},{"featureType":"poi.park","elementType":"all","stylers":[{"lightness":"-41"}]},{"featureType":"poi.school","elementType":"all","stylers":[{"visibility":"simplified"},{"hue":"#ff0000"},{"invert_lightness":true},{"saturation":"43"},{"lightness":"-16"},{"gamma":"0.73"}]},{"featureType":"poi.sports_complex","elementType":"all","stylers":[{"hue":"#ff0000"},{"saturation":"43"},{"lightness":"-11"},{"gamma":"0.73"},{"invert_lightness":true}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":"45"},{"lightness":"53"},{"gamma":"0.67"},{"invert_lightness":true},{"hue":"#ff0000"},{"visibility":"simplified"}]},{"featureType":"road","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"simplified"},{"hue":"#ff0000"},{"saturation":"38"},{"lightness":"-16"},{"gamma":"0.86"}]}],
	"Spy map": [{"featureType":"all","elementType":"geometry.fill","stylers":[{"visibility":"on"},{"saturation":"-66"},{"lightness":"1"}]},{"featureType":"all","elementType":"geometry.stroke","stylers":[{"visibility":"on"}]},{"featureType":"all","elementType":"labels","stylers":[{"visibility":"on"}]},{"featureType":"all","elementType":"labels.text.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"all","elementType":"labels.text.stroke","stylers":[{"color":"#000000"},{"lightness":13}]},{"featureType":"administrative","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"administrative","elementType":"geometry","stylers":[{"visibility":"on"}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#144b53"},{"lightness":14},{"weight":1.4}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#223c35"},{"visibility":"on"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#172720"},{"lightness":5},{"visibility":"on"}]},{"featureType":"poi","elementType":"geometry.fill","stylers":[{"visibility":"on"},{"color":"#162723"}]},{"featureType":"poi","elementType":"labels.text","stylers":[{"visibility":"on"}]},{"featureType":"poi","elementType":"labels.icon","stylers":[{"visibility":"on"}]},{"featureType":"road","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"road","elementType":"geometry","stylers":[{"visibility":"on"}]},{"featureType":"road","elementType":"geometry.fill","stylers":[{"visibility":"on"}]},{"featureType":"road","elementType":"geometry.stroke","stylers":[{"visibility":"on"},{"saturation":"14"},{"weight":"0.43"},{"color":"#357464"}]},{"featureType":"road","elementType":"labels","stylers":[{"visibility":"on"}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#1f3222"}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"lightness":25},{"color":"#133f19"}]},{"featureType":"road.highway","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"road.highway.controlled_access","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"road.highway.controlled_access","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"road.highway.controlled_access","elementType":"labels.text","stylers":[{"visibility":"on"}]},{"featureType":"road.arterial","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"road.arterial","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"road.arterial","elementType":"geometry.stroke","stylers":[{"lightness":16},{"color":"#1ad9ba"}]},{"featureType":"road.arterial","elementType":"labels.text","stylers":[{"visibility":"on"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"road.local","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"road.local","elementType":"geometry.fill","stylers":[{"color":"#26625a"}]},{"featureType":"road.local","elementType":"geometry.stroke","stylers":[{"visibility":"on"},{"color":"#48b697"}]},{"featureType":"road.local","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"color":"#233833"},{"visibility":"on"}]},{"featureType":"transit","elementType":"geometry.stroke","stylers":[{"visibility":"on"}]},{"featureType":"transit.line","elementType":"geometry.stroke","stylers":[{"visibility":"on"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#131d19"},{"visibility":"on"}]}],
	"Shades of Grey": [{"featureType":"all","elementType":"labels.text.fill","stylers":[{"saturation":36},{"color":"#000000"},{"lightness":40}]},{"featureType":"all","elementType":"labels.text.stroke","stylers":[{"visibility":"on"},{"color":"#000000"},{"lightness":16}]},{"featureType":"all","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#000000"},{"lightness":20}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#000000"},{"lightness":17},{"weight":1.2}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"color":"#000000"},{"lightness":20}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#000000"},{"lightness":21}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#000000"},{"lightness":17}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#000000"},{"lightness":29},{"weight":0.2}]},{"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#000000"},{"lightness":18}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#000000"},{"lightness":16}]},{"featureType":"transit","elementType":"geometry","stylers":[{"color":"#000000"},{"lightness":19}]},{"featureType":"water","elementType":"geometry","stylers":[{"color":"#000000"},{"lightness":17}]}],
	"Subtle Grayscale": [{"featureType":"landscape","stylers":[{"saturation":-100},{"lightness":65},{"visibility":"on"}]},{"featureType":"poi","stylers":[{"saturation":-100},{"lightness":51},{"visibility":"simplified"}]},{"featureType":"road.highway","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"road.arterial","stylers":[{"saturation":-100},{"lightness":30},{"visibility":"on"}]},{"featureType":"road.local","stylers":[{"saturation":-100},{"lightness":40},{"visibility":"on"}]},{"featureType":"transit","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"administrative.province","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":-25},{"saturation":-100}]},{"featureType":"water","elementType":"geometry","stylers":[{"hue":"#ffff00"},{"lightness":-25},{"saturation":-97}]}],
	"Blue water": [{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#46bcec"},{"visibility":"on"}]}],
	"Pale Dawn": [{"featureType":"administrative","elementType":"all","stylers":[{"visibility":"on"},{"lightness":33}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2e5d4"}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#c5dac6"}]},{"featureType":"poi.park","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":20}]},{"featureType":"road","elementType":"all","stylers":[{"lightness":20}]},{"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#c5c6c6"}]},{"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#e4d7c6"}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#fbfaf7"}]},{"featureType":"water","elementType":"all","stylers":[{"visibility":"on"},{"color":"#acbcc9"}]}],
	"Blue Essence": [{"featureType":"landscape.natural","elementType":"geometry.fill","stylers":[{"visibility":"on"},{"color":"#e0efef"}]},{"featureType":"poi","elementType":"geometry.fill","stylers":[{"visibility":"on"},{"hue":"#1900ff"},{"color":"#c0e8e8"}]},{"featureType":"road","elementType":"geometry","stylers":[{"lightness":100},{"visibility":"simplified"}]},{"featureType":"road","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"transit.line","elementType":"geometry","stylers":[{"visibility":"on"},{"lightness":700}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#7dcdcd"}]}],
	"Apple Maps-esque": [{"featureType":"landscape.man_made","elementType":"geometry","stylers":[{"color":"#f7f1df"}]},{"featureType":"landscape.natural","elementType":"geometry","stylers":[{"color":"#d0e3b4"}]},{"featureType":"landscape.natural.terrain","elementType":"geometry","stylers":[{"visibility":"off"}]},{"featureType":"poi","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"poi.business","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"poi.medical","elementType":"geometry","stylers":[{"color":"#fbd3da"}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#bde6ab"}]},{"featureType":"road","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#ffe15f"}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#efd151"}]},{"featureType":"road.arterial","elementType":"geometry.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"road.local","elementType":"geometry.fill","stylers":[{"color":"black"}]},{"featureType":"transit.station.airport","elementType":"geometry.fill","stylers":[{"color":"#cfb2db"}]},{"featureType":"water","elementType":"geometry","stylers":[{"color":"#a2daf2"}]}],
	"Midnight Commander": [{"featureType":"all","elementType":"labels.text.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"all","elementType":"labels.text.stroke","stylers":[{"color":"#000000"},{"lightness":13}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#144b53"},{"lightness":14},{"weight":1.4}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#08304b"}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#0c4152"},{"lightness":5}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#0b434f"},{"lightness":25}]},{"featureType":"road.arterial","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"road.arterial","elementType":"geometry.stroke","stylers":[{"color":"#0b3d51"},{"lightness":16}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#000000"}]},{"featureType":"transit","elementType":"all","stylers":[{"color":"#146474"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#021019"}]}],
	"Cool Grey": [{"featureType":"landscape","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"poi","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"stylers":[{"hue":"#00aaff"},{"saturation":-100},{"gamma":2.15},{"lightness":12}]},{"featureType":"road","elementType":"labels.text.fill","stylers":[{"visibility":"on"},{"lightness":24}]},{"featureType":"road","elementType":"geometry","stylers":[{"lightness":57}]}],
	"Neutral Blue": [{"featureType":"water","elementType":"geometry","stylers":[{"color":"#193341"}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"color":"#2c5a71"}]},{"featureType":"road","elementType":"geometry","stylers":[{"color":"#29768a"},{"lightness":-37}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#406d80"}]},{"featureType":"transit","elementType":"geometry","stylers":[{"color":"#406d80"}]},{"elementType":"labels.text.stroke","stylers":[{"visibility":"on"},{"color":"#3e606f"},{"weight":2},{"gamma":0.84}]},{"elementType":"labels.text.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"administrative","elementType":"geometry","stylers":[{"weight":0.6},{"color":"#1a3541"}]},{"elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#2c5a71"}]}],
	"Clean Cut": [{"featureType":"road","elementType":"geometry","stylers":[{"lightness":100},{"visibility":"simplified"}]},{"featureType":"water","elementType":"geometry","stylers":[{"visibility":"on"},{"color":"#C6E2FF"}]},{"featureType":"poi","elementType":"geometry.fill","stylers":[{"color":"#C5E3BF"}]},{"featureType":"road","elementType":"geometry.fill","stylers":[{"color":"#D1D1B8"}]}],
	"Red Hues": [{"stylers":[{"hue":"#dd0d0d"}]},{"featureType":"road","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"geometry","stylers":[{"lightness":100},{"visibility":"simplified"}]}],
	"Pastel Tones": [{"featureType":"landscape","stylers":[{"saturation":-100},{"lightness":60}]},{"featureType":"road.local","stylers":[{"saturation":-100},{"lightness":40},{"visibility":"on"}]},{"featureType":"transit","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"administrative.province","stylers":[{"visibility":"off"}]},{"featureType":"water","stylers":[{"visibility":"on"},{"lightness":30}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#ef8c25"},{"lightness":40}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"poi.park","elementType":"geometry.fill","stylers":[{"color":"#b6c54c"},{"lightness":40},{"saturation":-40}]},{}],
	"A Dark World": [{"stylers":[{"visibility":"simplified"}]},{"stylers":[{"color":"#131314"}]},{"featureType":"water","stylers":[{"color":"#131313"},{"lightness":7}]},{"elementType":"labels.text.fill","stylers":[{"visibility":"on"},{"lightness":25}]}],
	"Taste": [{"featureType":"water","elementType":"geometry","stylers":[{"color":"#a0d6d1"},{"lightness":17}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"color":"#ffffff"},{"lightness":20}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#dedede"},{"lightness":17}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#dedede"},{"lightness":29},{"weight":0.2}]},{"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#dedede"},{"lightness":18}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#ffffff"},{"lightness":16}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#f1f1f1"},{"lightness":21}]},{"elementType":"labels.text.stroke","stylers":[{"visibility":"on"},{"color":"#ffffff"},{"lightness":16}]},{"elementType":"labels.text.fill","stylers":[{"saturation":36},{"color":"#333333"},{"lightness":40}]},{"elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"geometry","stylers":[{"color":"#f2f2f2"},{"lightness":19}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#fefefe"},{"lightness":20}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#fefefe"},{"lightness":17},{"weight":1.2}]}],
	"Red Hat Antwerp": [{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"poi.business","elementType":"geometry.fill","stylers":[{"visibility":"on"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#b4d4e1"},{"visibility":"on"}]}],
	"Light Grey & Blue": [{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#dde6e8"},{"visibility":"on"}]}],
	"Muted": [{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"administrative.locality","elementType":"labels","stylers":[{"visibility":"on"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"},{"visibility":"simplified"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"poi","elementType":"geometry","stylers":[{"visibility":"simplified"},{"saturation":"-65"},{"lightness":"45"},{"gamma":"1.78"}]},{"featureType":"poi","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"poi","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road","elementType":"labels","stylers":[{"visibility":"on"}]},{"featureType":"road","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.highway","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit.line","elementType":"geometry","stylers":[{"saturation":"-33"},{"lightness":"22"},{"gamma":"2.08"}]},{"featureType":"transit.station.airport","elementType":"geometry","stylers":[{"gamma":"2.08"},{"hue":"#ffa200"}]},{"featureType":"transit.station.airport","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"transit.station.rail","elementType":"labels.text","stylers":[{"visibility":"off"}]},{"featureType":"transit.station.rail","elementType":"labels.icon","stylers":[{"visibility":"simplified"},{"saturation":"-55"},{"lightness":"-2"},{"gamma":"1.88"},{"hue":"#ffab00"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#bbd9e5"},{"visibility":"simplified"}]}],
	"TOR OP1": [{"featureType":"landscape","elementType":"geometry","stylers":[{"saturation":"-100"}]},{"featureType":"poi","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"poi","elementType":"labels.text.stroke","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"labels.text","stylers":[{"color":"#545454"}]},{"featureType":"road","elementType":"labels.text.stroke","stylers":[{"visibility":"off"}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"saturation":"-87"},{"lightness":"-40"},{"color":"#ffffff"}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"road.highway.controlled_access","elementType":"geometry.fill","stylers":[{"color":"#f0f0f0"},{"saturation":"-22"},{"lightness":"-16"}]},{"featureType":"road.highway.controlled_access","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"road.highway.controlled_access","elementType":"labels.icon","stylers":[{"visibility":"on"}]},{"featureType":"road.arterial","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"road.local","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"geometry.fill","stylers":[{"saturation":"-52"},{"hue":"#00e4ff"},{"lightness":"-16"}]}],
	"blueTacticle": [{"featureType":"all","elementType":"labels.text","stylers":[{"color":"#a1f7ff"}]},{"featureType":"all","elementType":"labels.text.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"all","elementType":"labels.text.stroke","stylers":[{"color":"#000000"},{"lightness":13}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#144b53"},{"lightness":14},{"weight":1.4}]},{"featureType":"administrative","elementType":"labels.text","stylers":[{"visibility":"simplified"},{"color":"#a1f7ff"}]},{"featureType":"administrative.province","elementType":"labels.text","stylers":[{"visibility":"simplified"},{"color":"#a1f7ff"}]},{"featureType":"administrative.locality","elementType":"labels.text","stylers":[{"visibility":"simplified"},{"color":"#a1f7ff"}]},{"featureType":"administrative.neighborhood","elementType":"labels.text","stylers":[{"visibility":"simplified"},{"color":"#a1f7ff"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#08304b"}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#0c4152"},{"lightness":5}]},{"featureType":"poi.attraction","elementType":"labels","stylers":[{"invert_lightness":true}]},{"featureType":"poi.attraction","elementType":"labels.text","stylers":[{"visibility":"simplified"},{"color":"#a1f7ff"}]},{"featureType":"poi.park","elementType":"labels","stylers":[{"visibility":"on"},{"invert_lightness":true}]},{"featureType":"poi.park","elementType":"labels.text","stylers":[{"visibility":"simplified"},{"color":"#a1f7ff"}]},{"featureType":"road","elementType":"labels.text","stylers":[{"color":"#a1f7ff"}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#0b434f"},{"lightness":25}]},{"featureType":"road.highway","elementType":"labels","stylers":[{"lightness":"0"},{"saturation":"0"},{"invert_lightness":true},{"visibility":"simplified"},{"hue":"#00e9ff"}]},{"featureType":"road.highway","elementType":"labels.text","stylers":[{"visibility":"simplified"},{"color":"#a1f7ff"}]},{"featureType":"road.highway.controlled_access","elementType":"labels.text","stylers":[{"color":"#a1f7ff"}]},{"featureType":"road.arterial","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"road.arterial","elementType":"geometry.stroke","stylers":[{"color":"#0b3d51"},{"lightness":16}]},{"featureType":"road.arterial","elementType":"labels","stylers":[{"invert_lightness":true}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#000000"}]},{"featureType":"road.local","elementType":"labels","stylers":[{"visibility":"simplified"},{"invert_lightness":true}]},{"featureType":"transit","elementType":"all","stylers":[{"color":"#146474"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#021019"}]}],
	"NightRider": [{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#1e242b"},{"lightness":"5"}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#1e242b"},{"saturation":"0"},{"lightness":"30"}]},{"featureType":"administrative","elementType":"labels","stylers":[{"color":"#1e242b"},{"lightness":"30"}]},{"featureType":"administrative","elementType":"labels.text.stroke","stylers":[{"visibility":"off"}]},{"featureType":"administrative.province","elementType":"geometry.stroke","stylers":[{"color":"#1e242b"},{"lightness":"20"},{"weight":"1.00"}]},{"featureType":"administrative.neighborhood","elementType":"labels.text.fill","stylers":[{"lightness":"-20"}]},{"featureType":"administrative.land_parcel","elementType":"labels.text.fill","stylers":[{"lightness":"-20"}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"color":"#1e242b"}]},{"featureType":"landscape","elementType":"labels","stylers":[{"color":"#1e242b"},{"lightness":"30"}]},{"featureType":"landscape","elementType":"labels.text.stroke","stylers":[{"visibility":"off"}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#1e242b"},{"lightness":"5"}]},{"featureType":"poi","elementType":"labels","stylers":[{"color":"#1e242b"},{"lightness":"30"}]},{"featureType":"poi","elementType":"labels.text.stroke","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"geometry","stylers":[{"visibility":"simplified"},{"color":"#1e242b"},{"lightness":"15"}]},{"featureType":"road","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"geometry","stylers":[{"color":"#1e242b"},{"lightness":"6"}]},{"featureType":"transit","elementType":"labels","stylers":[{"color":"#1e242b"},{"lightness":"30"}]},{"featureType":"transit","elementType":"labels.text.stroke","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"geometry","stylers":[{"color":"#010306"}]},{"featureType":"water","elementType":"labels.text.stroke","stylers":[{"visibility":"off"}]}],
	"Light and clean": [{"featureType":"administrative","elementType":"all","stylers":[{"visibility":"on"},{"lightness":33}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f7f7f7"}]},{"featureType":"poi.business","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#deecdb"}]},{"featureType":"poi.park","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":"25"}]},{"featureType":"road","elementType":"all","stylers":[{"lightness":"25"}]},{"featureType":"road","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#ffffff"}]},{"featureType":"road.highway","elementType":"labels","stylers":[{"saturation":"-90"},{"lightness":"25"}]},{"featureType":"road.arterial","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#ffffff"}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#ffffff"}]},{"featureType":"transit.line","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"transit.station","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"visibility":"on"},{"color":"#e0f1f9"}]}],
	"SAAB Navigation": [{"featureType":"all","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"all","elementType":"geometry","stylers":[{"color":"#004600"}]},{"featureType":"all","elementType":"labels.text","stylers":[{"saturation":"62"}]},{"featureType":"all","elementType":"labels.text.fill","stylers":[{"gamma":"1.81"},{"lightness":"100"},{"saturation":"100"},{"color":"#00ff0b"}]},{"featureType":"all","elementType":"labels.text.stroke","stylers":[{"saturation":"-100"},{"lightness":-33},{"weight":"2.53"},{"gamma":0.8},{"color":"#061d00"}]},{"featureType":"all","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"lightness":30},{"saturation":30}]},{"featureType":"landscape","elementType":"geometry.fill","stylers":[{"visibility":"on"},{"lightness":"-32"},{"saturation":"48"},{"color":"#000000"}]},{"featureType":"landscape.man_made","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"landscape.natural","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"landscape.natural.landcover","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"landscape.natural.terrain","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"poi","elementType":"geometry","stylers":[{"saturation":20}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"lightness":20},{"saturation":-20}]},{"featureType":"road","elementType":"geometry","stylers":[{"lightness":10},{"saturation":-30}]},{"featureType":"road","elementType":"geometry.fill","stylers":[{"lightness":"24"},{"saturation":"100"},{"color":"#39ff00"}]},{"featureType":"road","elementType":"geometry.stroke","stylers":[{"saturation":25},{"lightness":25}]},{"featureType":"road","elementType":"labels.text.fill","stylers":[{"color":"#2bff00"}]},{"featureType":"road","elementType":"labels.text.stroke","stylers":[{"color":"#000000"},{"weight":"4.46"}]},{"featureType":"transit","elementType":"geometry.fill","stylers":[{"saturation":"100"},{"lightness":"12"},{"color":"#148400"}]},{"featureType":"water","elementType":"all","stylers":[{"lightness":-20}]},{"featureType":"water","elementType":"geometry.fill","stylers":[{"lightness":"-100"},{"color":"#001a03"}]},{"featureType":"water","elementType":"geometry.stroke","stylers":[{"weight":"1.70"}]},{"featureType":"water","elementType":"labels.text.fill","stylers":[{"color":"#2bff00"}]}],
	"Light Gray & Light Blue": [{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f0f0f0"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"},{"color":"#ffffff"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#afdaec"},{"visibility":"on"}]}]
	/* https://snazzymaps.com/ */
}
var default_marker = {
	"width": 37,
	"height": 55,
	"top_offset": 54,
	"left_offset": 18,
	"binary": "iVBORw0KGgoAAAANSUhEUgAAACUAAAA3CAYAAACLgIOTAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAABx0RVh0U29mdHdhcmUAQWRvYmUgRmlyZXdvcmtzIENTNui8sowAAAcQSURBVGiBvZnvb1tXGcc/z/GP/HCThmVT7WQFGonB0qLBJNaQxuv6AiF1ztRXFVQIkHjDKyTQJrIWobIXwNqtL/gP6FQQGkJMdgYCJNrZbtqOgYr6g06wdLSNs/5S28SOE/uehxfOTe2ba8eOM76SJd9znvPcz33Ouc95ji2qSqvKJcZiIF8RYbfCToFBhU0C8wo3BM4qesoqfx5MZXKt+pdWoHKJsa8isl8gDnwaCDUwLwFXFdLAb2LJ9J82FCqXGNsnIi8DzzTr2EdnLfxsIJl+qy2omcRYvyC/EOFAGzA1UtUTFvu9wdTpuy1DzSTGnjIibwKf2SigKl1RZX8slf5n01C58V2jYFICn/gYgCpS7qKaiE5mptaEmn0+vh1DmjWAjAgioAq2yke99npgio7FUpnLdaFy47t6BPMu8NlGMACFUol8qcxCqUzJWlQVESEUMHQFg0RCQbpDlZdzDbhL4rBzy9vpebchWEOIOdYIKGCE/FKZW4UF8qUS1irLjAigQLEMD4pLGCNsCoV4tLuLSCiIUx9sWAP6GvDdFQ43UjPj8V0GMn6jBBARbhcWuFkoYBUCLk0DOaoYgS2Rbvq7ulBV6qIpo9FUegrAuG0GfaWevRHho3yB2fkCIE0BgQsu5OYLfJQvrEx9HaqfuN9EVcklxr4oIn/3dWyE24UiM3PzBIzB61ZhGvSCILdU9TFEdghs89jgWGWgJ8Kj3Z041j9e1uoXBiYz54MAgnzNz0hEWCiVuZkvrAZS/gP6Y1Hnrd1n/pV3m/8yOhwJYvYJvAIMVfxXHu5mvkAkFKIjGMAvFYmR/cB5ubZ3JBg0wbPA06uiJMK1uXnuFRe9U5a1qvv2TF287fvIwDuj2x9T5PfAqNvmqNLX2cHWnk31Fv7fTCA8YoImsNN9Im+UimWHucUlL9B1a3mhERDAs6cv3lL0BYUbbpsRYX5xiaLjIP7ra8hxFr9kFNkJ9Hl7DZAvlfzm//CeMxfq7lvVeu70xTvAwwUMlK1SWCo/fMNq9YigzxjxmTZXxXLZ23QH5bfNALlStW8CNQ+xsNpvlczTBhjw67IoJWvxRPny7qkL91uB2jN16R5wyb0WgbJ1sPUz1qBRpce3S/Ebll/d1JRqxtnGtj1GhAXfLhFWZ6XVa69J1YwzIshq364KBpj26zFAKGC80XryryOf39IKzckvD0eBYfdagZBPEq7StAF9D7+ZEugMBr2tvcbYb7UChci3oXaJdK3260oV3jOqmgHueHutKpFQiJDxRksOnRzd3lQ1empk+AlBDlbfMWQMkVCoXjlzCyVr6Ij8Q+GKH3JHwNAbDnsd9IJMnhoZ3t4I6OTojh2ImaQqSlaV3nCY8Opl4d71Smy2/7yoKrOJ+MsIP/WaiAhlx/LBvfuUrfXs8joPchTleL6Q/+/e89P21FPbDF2RT2H4JvASEKkGChrDUN9mggHju/ehOhFNZV4VVWUmsWubiHlfPEUfVPa/e4tLXH8wh4jvO7NIJdJ3gUeAzwHhmnsBqsrW3h42d4Tr7XsltfpEbDJzdaXImx2P/wr4up91wAh3CkVy85V007guqpU79bFNEfq7OhtVoCeiyfQ3oKrIU2sPgxb9rB2r9Hd1srW3h6AxOLZBPnb9AY61BI1ha29PYyCloFYPu5crULHJ7PvA0Xo3cVTZ3BFmqG8z/d1dBESwqjjLH+/3gAj93V0M9fU2mjJXR2OTmX+7FzWnmZm9o90SCFwW+GS90SKCAZasJb9UYqFcpmwtVsEIBM3yaSYcImwMFvwX9UqQ+NAplZ98/I9TKzvLqnNfLhE/IMKJRo8FlTLEiMDyGU9xDxiVO1mUZn47UTgQS6Z/XePb/4Qcz0pVxfgxKhtNpse8jf61lvIivkXCRkrVqn3Rr8cXKpZKT4GuOYVt6o2BVPaMX0edqhQEDgLz9frb1Bwqh+p11oXaksxcU7RuimhHCkeiqfT1lqHcwcCHG8x0Fcd5rZFBQ6iBZKaoqhMbSaQwEXv7tO/O4aqp3zxnx+NZNiJFKJloKh1fy6xhpB460++3DQSo8INm7JqCiqYy54A32iKC47Fk+t1mDJuLFAB6sFLYrUtzqD24tllFTUNFk5nrID9fD5Eqr0ZT2RtrW7YIBYDVY8DVFpmmkdLrrQxoCSo6mVnA0lqKUCZiyTMNU4BXLf0342p2PP4Olf9n1iJKR5OZZ1v139r0LcuqNlNFqAXfKmAtrQtqIJU5p+jxhkSqvxxIZs7936AAsHIIeFCn975FfrRe1+uGik2mb6hyxK9PVY8MptJNp4ANgwJwHPu6au2vNgofaFiPteO3LajH/5AtCvywuk1UJwZ+l20pBXi1rpTg1WwifhJhN+ipaDLzXLv+2orUilRfAm4Kuq4U4ONPN+ST2zv2nY3y9T/gjn2nPp+k9QAAAABJRU5ErkJggg=="
}
var hmapsprem_default_fonts = ['inherit', 'Arial', 'Verdana', 'Times New Roman', 'Times', 'Trebuchet MS', 'sans-serif', 'serif'];

//load front-end google fonts
function hmapsprem_load_frontend_fonts(font_family){
    //check font
    if(typeof font_family !== 'undefined' && font_family !== 'inherit'){
        //check if not default font
        if(jQuery.inArray(font_family,hmapsprem_default_fonts) == -1){
            var google_font_var = '<link href="https://fonts.googleapis.com/css?family='+ font_family +'" rel="stylesheet" type="text/css">';
        }
    }
    jQuery('head').append(google_font_var);
}

//initialise frontend
function hmapsprem_initialise_frontend(unique_name){
	//log the default object
	var map_object = eval("hmapsprem_default_object_"+ unique_name +"");
	hmapsprem_load_google_maps(map_object, unique_name);
}

//load google maps
function hmapsprem_load_google_maps(map_object,muid){
	//check if API already loaded
	if(!hmapsprem_loading_gmaps){
		//mark loading
		hmapsprem_loading_gmaps = true;
		if(typeof google === 'object' && typeof google.maps === 'object'){
			//mark google maps API loaded
			hmapsprem_map_loaded = true;
		}else{
			//load google maps API
			var script = document.createElement("script");
			script.type = "text/javascript";
			script.src = "https://maps.googleapis.com/maps/api/js?key="+ map_object.map_setup.api_key +"&libraries=places,drawing&callback=hmapsprem_map_initialiser";
			document.body.appendChild(script);
		}
	}
	//initialise map
	hmapsprem_initialise_map(map_object,muid);
}

//map initialiser
function hmapsprem_map_initialiser(){
	hmapsprem_map_loaded = true;
}

//initialise map
function hmapsprem_initialise_map(map_object,muid){
	if(hmapsprem_map_loaded){
		hmapsprem_inject_map(map_object,muid);
	}else{
		//loop until google maps API is present
		setTimeout(function(){
			hmapsprem_initialise_map(map_object,muid);
		},100);
	}
}

//inject map
function hmapsprem_inject_map(map_object,muid){
    //load google fonts
    hmapsprem_load_frontend_fonts(map_object.map_setup.font_family);
    //add class to map container
    jQuery('#hmapsprem_map_' + muid).addClass(map_object.map_developers.map_css_class);
    //set container size
    if(map_object.map_setup.responsive == "true"){
        var map_width = 100 + '%'
    }else{
        var map_width = parseInt(map_object.map_setup.map_width) + 'px'
    }
    jQuery('#hmapsprem_map_' + muid).css({
        'width':map_width, //check if responsive
        'height':map_object.map_setup.map_height + 'px'
    });
    //inject category selector(if required)
    if(map_object.map_settings.show_category_selector){
        //check type
        if(map_object.map_settings.category_selector_tabs == "false"){ //select object
            //create category selector
            var selector_html = '<select id="hmapsprem_category_selector_' + muid + '" class="category_selector ' + map_object.map_developers.category_selector_css_class + ' ' + map_object.map_settings.default_category_component_position + '" style="border:' + map_object.map_settings.category_selector_border_weight + 'px solid ' + map_object.map_settings.category_selector_border_colour + '; -webkit-border-radius:' + map_object.map_settings.category_selector_border_radius + 'px; -moz-border-radius:' + map_object.map_settings.category_selector_border_radius + 'px; border-radius:' + map_object.map_settings.category_selector_border_radius + 'px; padding:' + map_object.map_settings.category_selector_vert_padding + 'px ' + map_object.map_settings.category_selector_hor_padding + 'px; background-color:' + map_object.map_settings.category_selector_fill_colour + '; color: ' + map_object.map_settings.category_selector_font_colour + '; font-size: ' + map_object.map_settings.category_selector_font_size + 'px; font-weight:' + map_object.map_settings.category_selector_font_weight + ' px; font-family:'+ map_object.map_setup.font_family +';">';
            if(map_object.map_settings.default_display_category == "show_all"){
                selector_html += '<option value="show_all" selected>' + map_object.map_settings.show_category_selector_copy + '</option>';
            }else{
                selector_html += '<option value="show_all">' + map_object.map_settings.show_category_selector_copy + '</option>';
            }
            var default_sel = "uncategorised";
            jQuery.each(map_object.map_marker_categories, function(key, val){
                var mcount = 0;
                jQuery.each(map_object.map_markers, function(key1, val1){
                    if(val1.marker_category == val){
                        mcount++;
                    }
                });
                if(mcount > 0 && val != default_sel){
                    if(val == map_object.map_settings.default_display_category){
                        selector_html += '<option value="' + val + '" selected>' + val + '</option>';
                    }else{
                        selector_html += '<option value="' + val + '">' + val + '</option>';
                    }
                }
            });
            selector_html += '</select>';
            //check positioning
            if(map_object.map_settings.default_category_component_position == 'TOP_LEFT' || map_object.map_settings.default_category_component_position == 'TOP_RIGHT'){
                jQuery(selector_html).insertBefore('#hmapsprem_map_' + muid);
            }else{
                jQuery(selector_html).insertAfter('#hmapsprem_map_' + muid);
            }
            //bind category selection change
            jQuery('#hmapsprem_category_selector_' + muid).off().on('change', function(){
                //update visible map markers
                update_visible_map_markers(map_object, jQuery(this).val());
            });
        }else{ //tab object
            //create category selector
            var selector_html = '<div id="hmapsprem_tab_category_selector_' + muid + '" class="hmapsprem_cat_tab_container ' + map_object.map_developers.category_selector_css_class + '" style="background-color:' + map_object.map_settings.category_tab_bg_colour +'; padding:10px 0;">';
                selector_html += '</div>';
            //check positioning
            if(map_object.map_settings.default_category_tab_position == 'TOP'){
                jQuery(selector_html).insertBefore('#hmapsprem_map_' + muid);
            }else{
                jQuery(selector_html).insertAfter('#hmapsprem_map_' + muid);
            }
            //insert categories
            var default_sel = "uncategorised";
            var tab_html = '';
            jQuery.each(map_object.map_marker_categories, function(key, val){
                var mcount = 0;
                jQuery.each(map_object.map_markers, function(key1, val1){
                    if(val1.marker_category == val){
                        mcount++;
                    }
                });
                if(mcount > 0 && val != default_sel){
                    if(jQuery.inArray(val, map_object.map_settings.category_tab_default_categories) != -1){
                        jQuery('#hmapsprem_tab_category_selector_'+ muid).append('<div id="hmapsprem_tab_cat_sel_' + key + '" class="hmapsprem_cat_tab active"><a>' + val + '</a></div>');
                    }else{
                        jQuery('#hmapsprem_tab_category_selector_'+ muid).append('<div id="hmapsprem_tab_cat_sel_' + key + '" class="hmapsprem_cat_tab"><a>' + val + '</a></div>');
                    }
                    //bind event
                    jQuery('#hmapsprem_tab_category_selector_'+ muid +' #hmapsprem_tab_cat_sel_'+ key).off().on('click', function(){
                        manage_active_tab_state(map_object, this, val);
                    });
                }
            });
            jQuery('#hmapsprem_tab_category_selector_'+ muid).append('<div style="clear:both;"></div>');
            //apply styles
            update_example_category_tab_selector();
        }
    }
    //manage active tab state
    function manage_active_tab_state(map_object, elem, val){
        //check if currently active
        if(jQuery(elem).hasClass('active')){
            //deactivate
            jQuery(elem).removeClass('active');
            //remove from map
            var index = map_object.map_settings.category_tab_default_categories.indexOf(val);
            if(index > -1){
                map_object.map_settings.category_tab_default_categories.splice(index, 1);
            }
            update_visible_map_markers_tabs(map_object);
            //update style
            update_example_category_tab_selector();
        }else{
            //activate
            jQuery(elem).addClass('active');
            //add to map
            map_object.map_settings.category_tab_default_categories.push(val);
            update_visible_map_markers_tabs(map_object);
            //update style
            update_example_category_tab_selector();
        }
    }
    //update visible map markers (for tabs only)
    var first_tab_run = true;
    function update_visible_map_markers_tabs(map_object){
        if(map_object.map_advanced.marker_clustering){
            marker_cluster.clearMarkers();
        }
        jQuery.each(map_object.map_markers, function(key, val){
            //hide info windows on toggle
            if(map_object.iwp != null){
                map_object.iwp.setMap(null);
                map_object.iwp = null;
            }
            //update visible markers
            if(jQuery.inArray(val.marker_category, map_object.map_settings.category_tab_default_categories) != -1){
                //set visible
                val.gmp.setVisible(true);
                if(map_object.map_advanced.marker_clustering){
                    marker_cluster.addMarker(val.gmp);
                }
            }else{
                //hide
                val.gmp.setVisible(false);
            }
        });
        if(map_object.map_advanced.marker_clustering){
            marker_cluster.repaint();
            if(first_tab_run){
                first_tab_run = false;
                setTimeout(function(){
                    update_visible_map_markers_tabs(map_object);
                }, 200);
            }
        }
    }
    //apply tab styles
    function update_example_category_tab_selector(){
        //container
        jQuery('#hmapsprem_tab_category_selector_'+ muid +' .hmapsprem_cat_tab_container').css({
            'background-color': map_object.map_settings.category_tab_bg_colour
        });
        //inactive
        jQuery('#hmapsprem_tab_category_selector_'+ muid +' .hmapsprem_cat_tab').css({
            'font-size': map_object.map_settings.category_tab_font_size +'px',
            'line-height': map_object.map_settings.category_tab_font_size +'px',
            'font-weight': map_object.map_settings.category_tab_font_weight,
            'padding': map_object.map_settings.category_tab_vert_margin +'px '+ map_object.map_settings.category_tab_hor_margin +'px',
            'margin-right': 0
        });
        jQuery('#hmapsprem_tab_category_selector_'+ muid +' .hmapsprem_cat_tab a').css({
            'color': map_object.map_settings.category_tab_font_colour,
            'background-color': map_object.map_settings.category_tab_fill_colour,
            'padding': map_object.map_settings.category_tab_vert_padding +'px '+ map_object.map_settings.category_tab_hor_padding +'px',
            '-moz-border-radius': map_object.map_settings.category_tab_border_radius +'px',
            '-webkit-border-radius': map_object.map_settings.category_tab_border_radius +'px',
            'border-radius': map_object.map_settings.category_tab_border_radius +'px',
            'font-family': map_object.map_setup.font_family
        });
        //active
        jQuery('#hmapsprem_tab_category_selector_'+ muid +' .hmapsprem_cat_tab.active a').css({
            'color': map_object.map_settings.category_tab_font_active_colour,
            'background-color': map_object.map_settings.category_tab_active_fill_colour
        });
        //border (full/bottom only)
        if(map_object.map_settings.category_tab_border_bottom_only){
            //bottom only
            jQuery('#hmapsprem_tab_category_selector_'+ muid +' .hmapsprem_cat_tab a').css({
                'border': 'none',
                'border-bottom': map_object.map_settings.category_tab_border_weight +'px solid '+ map_object.map_settings.category_tab_border_colour
            });
            jQuery('#hmapsprem_tab_category_selector_'+ muid +' .hmapsprem_cat_tab.active a').css({
                'border': 'none',
                'border-bottom': map_object.map_settings.category_tab_border_weight +'px solid '+ map_object.map_settings.category_tab_border_active_colour
            });
        }else{
            //full border
            jQuery('#hmapsprem_tab_category_selector_'+ muid +' .hmapsprem_cat_tab a').css({
                'border': map_object.map_settings.category_tab_border_weight +'px solid '+ map_object.map_settings.category_tab_border_colour
            });
            jQuery('#hmapsprem_tab_category_selector_'+ muid +' .hmapsprem_cat_tab.active a').css({
                'border': map_object.map_settings.category_tab_border_weight +'px solid '+ map_object.map_settings.category_tab_border_active_colour
            });
        }
    }
    //initialise map
    latlng = eval("new google.maps.LatLng(" + map_object.map_settings.map_center + ");");
    var map_options = {
        zoom:map_object.map_advanced.map_load_zoom,
        scrollwheel:map_object.map_settings.mouse_wheel_zoom,
        center:latlng, //check for marker bounds - adjust center if required
        disableDefaultUI:true,
        mapTypeId:eval("google.maps.MapTypeId." + map_object.map_settings.map_type + ""),
        //map controls
        streetViewControl:map_object.map_controls.street_view,
        streetViewControlOptions:{
            position:eval("google.maps.ControlPosition." + map_object.map_controls.street_view_position + "")
        },
        mapTypeControl:map_object.map_controls.map_type,
        mapTypeControlOptions:{
            position:eval("google.maps.ControlPosition." + map_object.map_controls.map_type_position + ""),
            style:eval("google.maps.MapTypeControlStyle." + map_object.map_controls.map_type_style + "")
        },
        rotateControl:map_object.map_controls.rotate,
        rotateControlOptions:{
            position:eval("google.maps.ControlPosition." + map_object.map_controls.rotate_position + "")
        },
        zoomControl:map_object.map_controls.zoom,
        zoomControlOptions:{
            position:eval("google.maps.ControlPosition." + map_object.map_controls.zoom_position + "")
        },
        scaleControl:map_object.map_controls.scale
    };
    //load map
    var google_map = new google.maps.Map(document.getElementById("hmapsprem_map_" + muid), map_options);
    //map theme
    if(map_object.map_settings.map_theme){
        var theme = eval("map_themes['" + map_object.map_settings.map_theme + "']");
        google_map.setOptions({
            styles:theme
        });
    }
    //check if locate me control required
    if(map_object.map_controls.show_location){
        //construct custom controlvar
        locateMeControlDiv = document.createElement('div');
        new custom_my_location_control(locateMeControlDiv, google_map);
        locateMeControlDiv.index = 1;
        google_map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(locateMeControlDiv);
    }
    //markers
    var marker_cluster_arr = [];
    google.maps.event.addListener(google_map, "tilesloaded", function(){ //check for map load completion
        //remove listener
        google.maps.event.clearListeners(this, "tilesloaded");
        //call map initialised method
        if(typeof map_object.map_developers.map_initialised_method !== 'undefined' && map_object.map_developers.map_initialised_method !== ''){
            eval("" + map_object.map_developers.map_initialised_method + "();");
        }
        //place map markers
        var hmapsprem_info_window_pointer;
        map_object.iwp = hmapsprem_info_window_pointer;
        var cur_map_center;
        var cur_map_zoom;
        var bounds = new google.maps.LatLngBounds();
        //place markers after delay
        setTimeout(function(){
            var animation_timer = 0;
            var cur_marker_count = 0;
            var marker_count = (Object.keys(map_object.map_markers).length);
            var autofit = eval("map_object.map_settings.auto_fit");
            jQuery.each(map_object.map_markers, function(key, val){
                animation_timer = (animation_timer + map_object.map_advanced.marker_animation_timer);
                setTimeout(function(){
                    if(val.marker_id != null){
                        var marker_data = get_marker_data_from_object(val.marker_id, map_object.marker_data);
                        var width = marker_data.width;
                        var height = marker_data.height;
                        var top_offset = marker_data.top_offset;
                        var left_offset = marker_data.left_offset;
                        var img_binary = marker_data.img_binary;
                    }else{
                        var width = default_marker.width;
                        var height = default_marker.height;
                        var top_offset = default_marker.top_offset;
                        var left_offset = default_marker.left_offset;
                        var img_binary = default_marker.binary
                    }
                    //place marker
                    var icon_object = new google.maps.MarkerImage('data:image/png;base64,' + img_binary, new google.maps.Size(width, height), new google.maps.Point(0, 0), new google.maps.Point(left_offset, top_offset));
                    var latlng_object = val.latlng.split(',');
                    var latlng = new google.maps.LatLng(latlng_object[0], latlng_object[1]);
                    if(val.marker_category == map_object.map_settings.default_display_category || map_object.map_settings.default_display_category == "show_all"){
                        var marker_visible = true;
                    }else{
                        var marker_visible = false;
                    }
                    var map_marker = new google.maps.Marker({
                        position:latlng,
                        draggable:false,
                        icon:icon_object,
                        map:google_map,
                        animation:eval("google.maps.Animation." + map_object.map_advanced.marker_animation + ""),
                        title:map_object.map_advanced.tooltips ? val.title : null,
                        visible:marker_visible,
                        zIndex:2
                    });
                    marker_cluster_arr.push(map_marker);
                    //add marker pointer to map_object
                    val.gmp = map_marker;
                    //check if autfit
                    if(autofit){
                        bounds.extend(latlng);
                    }
                    //add marker click event listner
                    google.maps.event.addListener(map_marker, "click", function(){
                        //close info window if already open
                        if(hmapsprem_info_window_pointer != null){
                            hmapsprem_info_window_pointer.close();
                            hmapsprem_info_window_pointer = null;
                            map_object.iwp = null;
                        }else{
                            //get current map center and zoom
                            cur_map_center = google_map.getCenter();
                            cur_map_zoom = google_map.getZoom();
                        }
                        //set zoom
                        google_map.setZoom(map_object.map_advanced.marker_click_zoom);
                        //pan to marker
                        google_map.panTo(latlng);
                        //check if callback required
                        if(map_object.map_developers.javascript_callback){
                            if(typeof map_object.map_developers.javascript_callback !== 'undefined' && map_object.map_developers.javascript_callback !== '' && map_object.map_developers.callback_method != ''){
                                var extract = false;
                                if(eval("typeof " + map_object.map_developers.callback_method + " !== 'undefined'")){
                                    extract = true;
                                }
                                if(extract){
                                    //construct json object
                                    var json_object = {
                                        "marker_id":key,
                                        "location_title":val.title == '' ? null : val.title,
                                        "custom_param":val.custom_param == '' ? null : val.custom_param
                                    }
                                    eval("" + map_object.map_developers.callback_method + "(hmapsprem_extract_json('" + encodeURIComponent(JSON.stringify(json_object)) + "'));");
                                }
                            }
                        }
                        //check if info window required
                        if(val.info_window_show || val.link_show || map_object.map_settings.get_directions){
                            //create info window html
                            var info_window_html = '<div class="hmapsprem_info_window">';
                            info_window_html += '<h3 style="font-family:'+ map_object.map_setup.font_family +';">' + val.title + '</h3>';
                            if(val.info_window_show){
                                info_window_html += '<p style="font-family:'+ map_object.map_setup.font_family +';">';
                                info_window_html += nl2br(val.info_window_content);
                                info_window_html += '</p>';
                            }
                            if(val.link_show){
                                info_window_html += '<a href="' + val.link + '" target="' + val.link_target + '" style="color:' + val.link_colour + '; font-family:'+ map_object.map_setup.font_family +';">';
                                info_window_html += val.link_title;
                                info_window_html += '</a>';
                            }
                            info_window_html += '</div>';
                            if(val.link_show && map_object.map_settings.get_directions){
                                info_window_html += '<br>';
                            }
                            if(map_object.map_settings.get_directions){
                                info_window_html += '<div class="get_directions_btn" onclick="window.open(\'https://maps.google.com/maps?f=d&mrt=loc&t=m&saddr=My+Location&daddr=' + latlng.lat() + ',' + latlng.lng() + '\');">';
                                info_window_html += '<a style="font-family:'+ map_object.map_setup.font_family +';">';
                                info_window_html += 'Get Directions';
                                info_window_html += '</a>';
                                info_window_html += '</div>';
                            }
                            //add info window
                            var infowindow = new google.maps.InfoWindow({
                                content:info_window_html
                            });
                            //open info window
                            infowindow.open(google_map, map_marker);
                            //add info window object to array
                            hmapsprem_info_window_pointer = infowindow;
                            map_object.iwp = infowindow;
                            //detect close
                            google.maps.event.addListener(infowindow, "closeclick", function(){
                                //clear info window object
                                hmapsprem_info_window_pointer = null;
                                map_object.iwp = null;
                                //go back to prev pan and latlng on close
                                google_map.setCenter(cur_map_center);
                                google_map.setZoom(cur_map_zoom);
                            });
                        }
                    });
                    //fit bounds
                    cur_marker_count++;
                    if(autofit && cur_marker_count == marker_count){
                        setTimeout(function(){
                            if(cur_marker_count > 1){
                                google_map.fitBounds(bounds);
                            }else{
                                //default to single marker center
                                jQuery.each(map_object.map_markers, function(key, val){
                                    var latlng = val.latlng.split(',');
                                    var new_center = new google.maps.LatLng(latlng[0], latlng[1]);
                                    google_map.setCenter(new_center);
                                    google_map.setZoom(15);
                                    return false;
                                });
                            }
                        }, map_object.map_advanced.marker_drop_delay);
                    }
                    //fade in category selector
                    jQuery('.hmapsprem_container .category_selector').stop().animate({
                        'opacity':1
                    }, 300);
                    //enable marker clustering
                    if(cur_marker_count == marker_count){
                        setTimeout(function(){
                            if(map_object.map_settings.category_selector_tabs == "false"){
                                update_visible_map_markers(map_object, map_object.map_settings.default_display_category);
                            }else{
                                update_visible_map_markers_tabs(map_object);
                            }
                        }, map_object.map_advanced.marker_drop_delay);
                    }
                }, animation_timer);
            });
            //center map
            if(!autofit){
                var latlng_object = map_object.map_settings.map_center.split(',');
                var latlng = new google.maps.LatLng(latlng_object[0], latlng_object[1]);
                google_map.setCenter(latlng);
                google_map.setZoom(map_object.map_settings.rest_zoom);
            }
        }, map_object.map_advanced.marker_drop_delay);
    });
    //shapes
    setTimeout(function(){
        jQuery.each(map_object.map_poly, function(key, val){
            switch(val.type){
                case 'polyline':
                    //get polyline data
                    var draw_path = [];
                    jQuery.each(val.path, function(k, v){
                        var latlng = v.split(',');
                        draw_path.push(new google.maps.LatLng(latlng[0], latlng[1]));
                    });
                    var polylineOptions = {
                        path:draw_path,
                        strokeColor:val.strokeColor,
                        strokeOpacity:val.strokeOpacity,
                        strokeWeight:val.strokeWeight,
                        geodesic:val.geodesic,
                        map:google_map,
                        draggable:false,
                        clickable:false,
                        editable:false,
                        zIndex:1
                    };
                    //place circle on map
                    polyline = new google.maps.Polyline(polylineOptions);
                    break;
                case 'circle':
                    //get circle data
                    var latlng = val.latlng.split(',');
                    var circleOptions = {
                        strokeColor:val.strokeColor,
                        strokeOpacity:val.strokeOpacity,
                        strokeWeight:val.strokeWeight,
                        fillColor:val.fillColor,
                        fillOpacity:val.fillOpacity,
                        map:google_map,
                        center:new google.maps.LatLng(latlng[0], latlng[1]),
                        radius:val.radius,
                        draggable:false,
                        clickable:false,
                        editable:false,
                        zIndex:1
                    };
                    //place circle on map
                    circle = new google.maps.Circle(circleOptions);
                    break;
                case 'polygon':
                    //get polygon data
                    var draw_path = [];
                    jQuery.each(val.path, function(k, v){
                        var latlng = v.split(',');
                        draw_path.push(new google.maps.LatLng(latlng[0], latlng[1]));
                    });
                    var polygonOptions = {
                        path:draw_path,
                        strokeColor:val.strokeColor,
                        strokeOpacity:val.strokeOpacity,
                        strokeWeight:val.strokeWeight,
                        fillColor:val.fillColor,
                        fillOpacity:val.fillOpacity,
                        map:google_map,
                        draggable:false,
                        clickable:false,
                        editable:false,
                        zIndex:1
                    };
                    //place polygon on map
                    polygon = new google.maps.Polygon(polygonOptions);
                    break;
                case 'rectangle':
                    //get rectangle data
                    var ne_latlng = val.NE.split(',');
                    var sw_latlng = val.SW.split(',');
                    var NE = new google.maps.LatLng(ne_latlng[0], ne_latlng[1]);
                    var SW = new google.maps.LatLng(sw_latlng[0], sw_latlng[1])
                    var draw_bounds = new google.maps.LatLngBounds(SW, NE);
                    var rectangleOptions = {
                        bounds:draw_bounds,
                        strokeColor:val.strokeColor,
                        strokeOpacity:val.strokeOpacity,
                        strokeWeight:val.strokeWeight,
                        fillColor:val.fillColor,
                        fillOpacity:val.fillOpacity,
                        map:google_map,
                        draggable:false,
                        clickable:false,
                        editable:false,
                        zIndex:1
                    };
                    //place rectangle on map
                    rectangle = new google.maps.Rectangle(rectangleOptions);
                    break;
            }
        });
    }, map_object.map_advanced.shape_drop_delay);
    //check map search required
    if(map_object.map_settings.frontend_search){
        //inject map search box
        var search_html = '<div class="hero_map_search_bar">';
        search_html += '<input class="location_search_input" id="location_search_' + muid + '" type="text" placeholder="Search Map" style="font-family:Arial;" />'; //style="font-family:'+ map_object.map_setup.font_family +';"
            search_html += '<div class="search_icon"></div>';
        search_html += '</div>';
        jQuery('#hmapsprem_map_' + muid).append(search_html);
        //enable map search
        var input = document.getElementById('location_search_' + muid);
        var autocomplete = new google.maps.places.Autocomplete(input);
        autocomplete.bindTo('bounds', google_map);
        google.maps.event.addListener(autocomplete, 'place_changed', function(){
            var place = autocomplete.getPlace();
            //place marker
            if(typeof map_search_marker != 'undefined'){
                map_search_marker.setMap(null);
                map_search_marker = undefined;
            }
            var icon_object = {
                url: hmapsprem_url + 'assets/images/search_marker.png',
                size: new google.maps.Size(41, 26),
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(21, 12)
            };
            map_search_marker = new google.maps.Marker({
                position: place.geometry.location,
                draggable: false,
                raiseOnDrag: false,
                icon: icon_object,
                map: google_map,
                zIndex: 2
            });
            if(typeof place.geometry != 'undefined'){
                if(place.geometry.viewport){
                    google_map.fitBounds(place.geometry.viewport);
                }else{
                    google_map.setCenter(place.geometry.location);
                    google_map.setZoom(17);
                }
            }
        });
        //manage search width based on map width
        resize_search_input(google_map, muid);
        jQuery(window).resize(function(){
            resize_search_input(google_map, muid);
        });
        //detect street view active
        var thePanorama = google_map.getStreetView();
        google.maps.event.addListener(thePanorama, 'visible_changed', function(){
            if(thePanorama.getVisible()){
                //active - hide search
                jQuery('#hmapsprem_map_' + muid + ' .hero_map_search_bar').fadeOut(300);
            }else{
                //inactive - show search
                jQuery('#hmapsprem_map_' + muid + ' .hero_map_search_bar').fadeIn(300);
            }
        });
    }
    //maintain map center on resize
    var center;

    function calculateCenter(){
        center = google_map.getCenter();
    }

    google.maps.event.addDomListener(google_map, 'idle', function(){
        calculateCenter();
    });
    //bind window resize pan lock
    if(map_object.map_settings.mobile_pan_lock){
        //check if draggable lock required
        if(jQuery(window).width() <= map_object.map_settings.mobile_pan_lock_width){
            //lock draggable
            google_map.setOptions({
                draggable:false
            });
        }
        //bind to window resize
        jQuery(window).resize(function(){
            //get widow width
            var window_width = jQuery(window).width();
            //check if window width < mobile_pan_lock_width
            if(window_width <= map_object.map_settings.mobile_pan_lock_width){
                //lock draggable
                google_map.setOptions({
                    draggable:false
                });
            }else{
                //unlock draggable
                google_map.setOptions({
                    draggable:true
                });
            }
        });
    }
    //change to detect map holder resize as opposed to a window resize
    var map_div = document.getElementById('hmapsprem_map_' + muid);
    google.maps.event.addDomListener(map_div, 'resize', function(){
        google_map.setCenter(center);
    });
    //enable marker clustering
    if(map_object.map_advanced.marker_clustering){
        var marker_cluster_options = {gridSize:50, maxZoom:15, ignoreHidden:true};
        var marker_cluster = new MarkerClusterer(google_map, [], marker_cluster_options)
    }
    //update visible map markers
    var first_run = true;
    function update_visible_map_markers(map_object, category){
        if(map_object.map_advanced.marker_clustering){
            marker_cluster.clearMarkers();
        }
        jQuery.each(map_object.map_markers, function(key, val){
            //hide info windows on toggle
            if(map_object.iwp != null){
                map_object.iwp.setMap(null);
                map_object.iwp = null;
            }
            //update visible markers
            if(val.marker_category == category || category == "show_all"){
                //set visible
                val.gmp.setVisible(true);
                if(map_object.map_advanced.marker_clustering){
                    marker_cluster.addMarker(val.gmp);
                }
            }else{
                //hide
                val.gmp.setVisible(false);
            }
        });
        if(map_object.map_advanced.marker_clustering){
            marker_cluster.repaint();
            if(first_run){
                first_run = false;
                setTimeout(function(){
                    update_visible_map_markers(map_object, category);
                }, 200);
            }
        }
    }
}

//custom my location control
var custom_my_location_visible = false;
function custom_my_location_control(container, map){
    //check if already visible
    if(!custom_my_location_visible){
        custom_my_location_visible = true;
        //construct control
        var controlUI = document.createElement('div');
        controlUI.style.width = '29px';
        controlUI.style.height = '29px';
        controlUI.style.backgroundColor = '#FFF';
        controlUI.style.marginRight = '9px';
        controlUI.style.boxShadow = '0 1px 2px rgba(0,0,0,.2)';
        controlUI.style.borderRadius = '3px';
        controlUI.style.cursor = 'pointer';
        //append control to container
        container.appendChild(controlUI);
        //cnstruct control inner
        var controlInternal = document.createElement('div');
        controlInternal.innerHTML = '<img src="' + hmapsprem_url + 'assets/images/locate_me.png">';
        //append control inner
        controlUI.appendChild(controlInternal);
        //bind event listener
        controlUI.addEventListener('click', function(){
            geolocate_user(map);
        });
    }
}

//geolocate user
function geolocate_user(map){
    if(navigator.geolocation){
        navigator.geolocation.getCurrentPosition(
            geolocationSuccess, null
        );
    }
    function geolocationSuccess(position){
        var location = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
        map.setCenter(location);
        map.setZoom(12);
    }
}

//resize search input
function resize_search_input(map, muid){
    ////get map width
    var map_width = jQuery('#hmapsprem_map_'+ muid).width();
    var search_width = 350;
    if(map_width < 380){
        search_width = 200;
    }else if(map_width < 450){
        search_width = 300;
    }
    //set width
    jQuery('#hmapsprem_map_'+ muid + ' .hero_map_search_bar').css({
        'width': search_width +'px'
    });
    jQuery('#hmapsprem_map_'+ muid + ' .hero_map_search_bar .location_search_input').css({
        'width': search_width +'px'
    });
}

//get marker data from map_markers_object
function get_marker_data_from_object(marker_id, marker_data_arr){
	//loop object
	var marker_data;
	jQuery.each(marker_data_arr.categories, function(key,val){
		jQuery.each(val.links, function(key,val){
			jQuery.each(val.markers, function(key,val){
				if(val.marker_id == marker_id){
					marker_data = val;
					return false;
				}
			});
		});
	});
	return marker_data;
}

//extract json object
function hmapsprem_extract_json(json){
	if(json !== 'undefined'){
		return JSON.parse(decodeURIComponent(json));
	}
	return false;
}

//nl2br
function nl2br(str, is_xhtml){
	var breakTag = (is_xhtml || typeof is_xhtml === 'undefined') ? '<br />' : '<br>';
	return (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1' + breakTag + '$2');
}