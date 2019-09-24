// toolbar.js
.pragma library

var filePrefix = "file://"
var pathToAssets = "/production/assets/"
var pathToProject = "/texture/main/"
var pathToCache = pathToProject + "cache/"
var fbxPostfix = "_texture_main.fbx"
var savePostfix = "_project.spp"

// Documentation for substance painter's 'alg' functions:
// file:///opt/Allegorithmic/Substance_Painter/resources/javascript-doc/alg.html

function save(assetName, mediaDir) {
  alg.log.info("saving " + assetName)
  var filePath = filePrefix + mediaDir + pathToAssets + assetName + pathToProject + assetName + savePostfix
  alg.log.info(filePath)

  alg.project.save(filePath, alg.project.SaveMode.Incremental)
}

function load(assetName, mediaDir) {
  alg.log.info("loading " + assetName)
  var filePath = filePrefix + mediaDir + pathToAssets + assetName + pathToProject + assetName + savePostfix
  alg.log.info(filePath)
  customSaveAndClose(mediaDir)

  alg.project.open(filePath)
}

function importFile(assetName, mediaDir) {
  alg.log.info("importing " + assetName)
  var fbxPath = filePrefix + mediaDir + pathToAssets + assetName + pathToCache + assetName + fbxPostfix
  customSaveAndClose(mediaDir)

  alg.project.create(fbxPath)
}

function exportMaps(assetName, mediaDir) {
  alg.log.info("opening dialogue to export " + assetName)
  var exportPath = mediaDir + pathToAssets + assetName + pathToCache

  alg.mapexport.showExportDialog({format:"png", path:exportPath})
}

// Helper function for saving and closing a file
function customSaveAndClose(mediaDir) {
  alg.log.info("customSaveAndClose")
  // Break early if nothing needs to be saved
  if (!alg.project.isOpen()) {
    alg.log.info("no project opened--skipping save step")
    return
  }

  // Check if the "default" project is still open from having passed in the mediaDir as an arg at sbs painter startup.
  if (alg.project.name() === mediaDir.split("/").pop() ) {
    alg.log.info("closing default project")
    alg.project.close()
  }
  // Save an already opened file
  else {
    alg.log.info("saving and closing current project")
    alg.project.saveAndClose()
  }
}
