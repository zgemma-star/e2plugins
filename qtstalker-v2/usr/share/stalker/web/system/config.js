/**
 * System configuration
 */

'use strict';

/* jshint unused:false */

var configuration = (function () {
	var config = {
		newRemoteControl: false,
		allowMulticastUpdate: false
	},
		control = null;

	config.newRemoteControl = [
		'AuraHD2', 'AuraHD3', 'AuraHD8', 'MAG275', 'MAG276', 'WR320'
	].indexOf(gSTB.GetDeviceModelExt()) !== -1;

	try{
		control = JSON.parse(gSTB.GetEnv('{"varList":["controlModel"]}'));
		if ( !control.errMsg && control.result && control.result.controlModel ) {
			if ( control.result.controlModel === 'SRC4513' ) {
				config.newRemoteControl = true;
			} else {
				config.newRemoteControl = false;
			}
		}
	} catch (e) {
		echo(e ,'controlModel parse')
	}

	return config;
})();
