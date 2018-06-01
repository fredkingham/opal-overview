module.exports = function(config){
  var opalPath = process.env.OPAL_LOCATION;
  var karmaDefaults = require(opalPath + '/opal/tests/js_config/karma_defaults.js');
  var baseDir = __dirname + '/..';
  var coverageFiles = [
    __dirname+'/../overview/static/js/overview/**/*.js',
  ];
    var includedFiles = [
      __dirname+'/../overview/static/js/overview/**/*.js',
      __dirname+'/../overview/static/js/test/*.js',
  ];

  var defaultConfig = karmaDefaults(includedFiles, baseDir, coverageFiles);
  config.set(defaultConfig);
};