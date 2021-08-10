/* Constantes globales */
const SELECTED_DISTRICT_COLOR = "green";
const PROVINCE_SELECT_OPACITY = "0.4";
const CANTON_SELECT_OPACITY = "0.7";
const DISTRICT_SELECT_STROKE = "black";
const DISTRICT_DEFAULT_STROKE = "rgb(216, 161, 104)";
const DISTRICT_SELECTED_STROKE_WIDTH = "8";
const DISTRICT_DEFAULT_STROKE_WIDTH = "5.60736";
const COLOR_TRANSPARENT = "rgba(0,255,0,0)";
const LAYER_ALERTA = 3;
const LAYER_SS = 4;
const LAYER_SEDES = 5;
const LAYER_PARADAS = 6;
const LAYER_HOGARES = 7;
const LAYER_INDIGENAS = 8;
const LAYER_FUENTES = 9;
const LAYER_MORBILIDAD = 10;
const LAYER_PROY_DIST_15 = 11;
const LAYER_PROY_DIST_20 = 12;
const LAYER_PROY_DIST_40 = 13;
const LAYER_PROY_DIST_50 = 14;

/* Variables globales */
var _selectedProvince;
var _selectedCanton;
var _selectedDistrito;
var _originalDistrictColor;
var _mapa;
var _resizer;
var _selectedLayer;
var _layerParadas;
var _layerSedes;
var _layerHogares;
var _layerIndigenas;
var _layerFuentes;
var _layerMorbilidad;
var _prediccionesMapa;
var _ultimaFecha;
var _datosMorbilidad = {};
var _legend;
var _fechaActual;
var _layer_actual;
var _fechasValidas = [];
var _wide_screen;

/* Inicialización de variables */
provincias = new L.FeatureGroup();
provLayer = null;
cantones = new L.FeatureGroup();
distritos = new L.FeatureGroup();
_layerParadas = null;
_layerSedes = null;
_layerHogares = null;
_layerFuentes = null;
_layerMorbilidad = null;
var map = null;
var circulosMorbilidad = null;

/* Capa base del mapa */
var u0 =
  "https://{s}.tile.jawg.io/jawg-light/{z}/{x}/{y}{r}.png?access-token=XF87Xv2CrTh3C1C4ApZvDyWQTZoiSaVBGvmI0cG5tXJqXj5AVPxAQSSP20JXrjFw";
  
var u1 =
  "https://{s}.tile.jawg.io/jawg-streets/{z}/{x}/{y}{r}.png?access-token=XF87Xv2CrTh3C1C4ApZvDyWQTZoiSaVBGvmI0cG5tXJqXj5AVPxAQSSP20JXrjFw";

var u2 =
  "https://{s}.tile.jawg.io/jawg-terrain/{z}/{x}/{y}{r}.png?access-token=XF87Xv2CrTh3C1C4ApZvDyWQTZoiSaVBGvmI0cG5tXJqXj5AVPxAQSSP20JXrjFw";

var urltile = [u0, u1, u2];

var contri =
  '<a href="http://jawg.io" title="Tiles Courtesy of Jawg Maps" target="_blank">&copy; <b>Jawg</b>Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

/* Configuración de Toastr */
toastr.options = {
  "closeButton": false,
  "debug": false,
  "newestOnTop": false,
  "progressBar": false,
  "positionClass": "toast-top-center",
  "preventDuplicates": false,
  "onclick": null,
  "showDuration": "300",
  "hideDuration": "1000",
  "timeOut": "5000",
  "extendedTimeOut": "1000",
  "showEasing": "swing",
  "hideEasing": "linear",
  "showMethod": "slideDown",
  "hideMethod": "slideUp",
  "tapToDismiss": true
}

/**INICIALIZADOR**/
window.onload = function () {
  $.noConflict();

  /** Código para hacer las columnas ajustables, solo si el viewport es de 1700px de ancho o más. */
  const GUTTER_SIZE = 2;

  if (window.matchMedia("(min-width: 1700px)").matches) {
    _wide_screen = true;

    const gutterStyle = (dimension) => ({
      "flex-basis": `${GUTTER_SIZE}px`,
    });

    const elementStyle = (dimension, size, gutSize, i) => ({
      "flex-basis": `calc(${size}% - ${GUTTER_SIZE}px)`,
      width: size + "%",
    });

    Split(["#col-mapa", "#col-graficos", "#col-indicadores"], {
      sizes: [38, 25, 33],
      minSize: 10,
      elementStyle,
      gutterStyle,
    });
  } else {
    _wide_screen = false;
  }

  initMap();

  let url = "get_leaflet_dist";

  $.get("getValidDates", function(result){
    _fechasValidas = result.fechas;
    $.get("getUltimaFecha", function(result){
      _ultimaFecha = result.date[0];
      _fechaActual = _ultimaFecha;
      getDatosPais();
      changeGauge(null, null, null);
      $.get(url, { date: _ultimaFecha }, function (result) {
        let datos_json = JSON.parse("[" + result["capas"] + "]");
        configurar_mapa(map, datos_json);
        $('input[name="datepicker"]').daterangepicker(
          {
            singleDatePicker: true,
            locale: {
              format: "DD/MM/YYYY",
              separator: " - ",
              applyLabel: "Aceptar",
              cancelLabel: "Cancelar",
              fromLabel: "Desde",
              toLabel: "Hasta",
              customRangeLabel: "Personalizado",
              weekLabel: "S",
              daysOfWeek: ["D", "L", "K", "M", "J", "V", "S"],
              monthNames: [
                "Enero",
                "Febrero",
                "Marzo",
                "Abril",
                "Mayo",
                "Junio",
                "Julio",
                "Agosto",
                "Septiembre",
                "Octubre",
                "Noviembre",
                "Diciembre",
              ],
              firstDay: 1
            },
            isInvalidDate: function(ele){
              /* Se encarga de deshabilitar las fechas en las que no hay datos en la base de datos. */
              let currDate = moment(ele._d).format('YYYY-MM-DD');
              return !_fechasValidas.includes(currDate);
            },
            startDate: parseDate(_ultimaFecha),
            minDate: "06/03/2020",
            maxDate: parseDate(_ultimaFecha),
          },
          function (start, end, label) {
            _fechaActual = start.format("YYYY-MM-DD");
            setDate(_fechaActual);
            getDatosPais();
            $("#mapas").multiselect('enable');
            $("#mapas").multiselect('deselectAll');
            $("#mapas").multiselect('rebuild');
            $("#mapas").multiselect('refresh');
            $("#provincias").removeAttr('disabled');
            $("#cantones").removeAttr('disabled');
            $("#distritos").removeAttr('disabled');
            _selectedLayer = null;
          }
        );
      });
    });
  });

  /* Para cada valor seleccionado en el multiselect, pinta los colores o elementos de la capa correspondiente */
  $("#mapas").on("change", function () {
    let temp = $(this).val();
    setLayers(temp);
    if(_selectedLayer != null && _selectedLayer.length > 0){
      $("#provincias").attr('disabled', 'disabled');
      $("#cantones").attr('disabled', 'disabled');
      $("#distritos").attr('disabled', 'disabled');
    } else {
      $("#provincias").removeAttr('disabled');
      $("#cantones").removeAttr('disabled');
      $("#distritos").removeAttr('disabled');
    }
  });

  $("#mapas").multiselect({
    includeSelectAllOption: true,
    optionClass: function (element) {
      var value = $(element).val();
      if (value % 2 == 0) {
        return "odd"; // reversed
      } else {
        return "even"; // reversed
      }
    },
    buttonContainer: '<div class="" />',
    buttonClass: "form-control",
    nonSelectedText: "Seleccione",
    allSelectedText: "Todas",
    selectAllText: "Todas",
    nSelectedText: "seleccionadas",
    numberDisplayed: 1,
  });

  /*Coloca la fecha en el formato DD/MM/YYYY HH:MM:SS */
  function timerDaemon() {
    var today = new Date();
    $("#hora").html(
      today.getDate() +
        "/" +
        (today.getMonth() + 1) +
        "/" +
        today.getFullYear() +
        " " +
        (today.getHours() < 10 ? "0" + today.getHours() : today.getHours()) +
        ":" +
        (today.getMinutes() < 10
          ? "0" + today.getMinutes()
          : today.getMinutes()) +
        ":" +
        (today.getSeconds() < 10
          ? "0" + today.getSeconds()
          : today.getSeconds())
    );
  }
  setInterval(timerDaemon, 1000);

  /**
   * Colorea de azul la provincia seleccionada en el select.
   * Baja la opacidad de las demás provincias para resaltar la seleccionada.
   * Limpia los datos de variables globales cuando ya no se van a usar.
   */

  $("#provincias").on("change", function () {
    if (_selectedLayer != null && _selectedLayer.length > 0) {
      $(this).val("none");
      toastr.warning("Elimine las vistas del mapa antes de seleccionar una provincia.", "Advertencia");
      return;
    }
    let originalSelectedProvince = $("#provincias").val();
    _selectedCanton = null;
    let selectedProvince = $("#provincias")
      .val()
      .toUpperCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
    if (selectedProvince != "NONE") {
      _selectedProvince = selectedProvince;
      $("#mapas").multiselect('disable');
    } else {
      _selectedProvince = null;
      $("#mapas").multiselect('enable')
    }
    _layer_actual.eachLayer(function (layer) {
      if (layer.feature.properties.proinfo !== undefined) {
        nombP = layer.feature.properties.proinfo;
        if (nombP.toUpperCase() == selectedProvince) {
          layer.setStyle({ fillColor: "rgba(0, 0, 255, 0.3)" });
          layer.setStyle({ fillOpacity: 0.8 });
        } else {
          layer.setStyle({ fillColor: "rgba(255, 0, 0, 0.0)" });
        }
      }
    });
    if (selectedProvince != "NONE") {
      changeCantones(originalSelectedProvince);
      changeGauge(selectedProvince);
    } else {
      _selectedProvince = null;
      changeGauge("");
    }
    clearSelectList($("#cantones"), "none", "-- Seleccione provincia --");
    clearSelectList($("#distritos"), "none", "-- Seleccione cantón --");
    _selectedCanton = null;
    _selectedDistrito = null;
  });

  /*check orden o animado*/
  $("input:radio[name=radio-group-1-bg]").change(function () {
    let value = this.value;

    if (value == "orden") {
      tipo = 1;
    } else {
      tipo = 2;
    }
    changeGauge(_selectedProvince, _selectedCanton, _selectedDistrito, tipo)
  });

  $("input:radio[name='radio_sems']").change(function () {
    let eleccion = $(".eleccion input:checked").val();
    if(eleccion == 'sem0'){
      $("#provincias").removeAttr('disabled');
      $("#cantones").removeAttr('disabled');
      $("#distritos").removeAttr('disabled');
    } else {
      $("#cases-dashboard p.data:not(.pais)").html(
        "--"
      );
      getPredicciones(eleccion);
      $("#provincias").attr('disabled', 'disabled');
      $("#cantones").attr('disabled', 'disabled');
      $("#distritos").attr('disabled', 'disabled');
    }
  });

  $("#cantones").on("change", function () {
    if (_selectedLayer != null && _selectedLayer.length > 0) {
      $(this).val("none");
      toastr.warning("Elimine las vistas del mapa antes de seleccionar un cantón.", "Advertencia");
      return;
    }
    let selectedCanton = $("#cantones")
      .val()
      .toUpperCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
    _selectedCanton = selectedCanton;
    changeDistritos(_selectedCanton);
    _layer_actual.eachLayer(function (layer) {
      if (
        layer.feature.properties.proinfo !== undefined &&
        layer.feature.properties.cantinfo !== "--Todos--"
      ) {
        nombP = layer.feature.properties.proinfo;
        nombC = layer.feature.properties.cantinfo;

        if (nombP.toUpperCase() == _selectedProvince) {
          layer.setStyle({ fillColor: "rgba(0, 0, 255, 0.3)" });
          layer.setStyle({ fillOpacity: 0.8 });
          if (nombC.toUpperCase() == selectedCanton) {
            layer.setStyle({ fillColor: "rgba(255, 0, 0, 0.5)" });
          }
        } else {
          layer.setStyle({ fillColor: COLOR_TRANSPARENT });
        }
      } else {
        _selectedCanton = null;
      }
    });
  });

  $("#distritos").on("change", function () {
    if (_selectedLayer != null && _selectedLayer.length > 0) {
      $(this).val("none");
      toastr.warning("Elimine las vistas del mapa antes de seleccionar un distrito.", "Advertencia");
      return;
    }
    let selectedDistrito = $("#distritos")
      .val()
      .toUpperCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
    _selectedDistrito = selectedDistrito;
    seleccionarDistrito(_selectedDistrito);
    changeGauge(_selectedProvince, _selectedCanton, selectedDistrito);
  });

  loadXMLMap("getMap");

  setUpCreditsBubbles();
}; //FIN INICIALIZADOR

$("input[data-provide=datepicker]").on("click", function () {
  $(".datepicker.datepicker-dropdown").css("z-index", "1000");
});

/**
 * Obtiene las predicciones para todos los cantones en una semana dada, en el mes de la fecha seleccionada en el datepicker,
 * y guarda los datos en un JSON en una variable global.
 * @param {*} semana Semana de predicciones: I, II, III, IV, o V.
 */
function getPredicciones(semana){
  let mes = parseInt($("[name='datepicker']").val().split('/')[1]);
  let url = 'getPrediccionesMapa';
  $.get(url, {mes: mes, semana: semana}, function(result){
    _prediccionesMapa = result.predicciones;
  });
}

function onEachFeature(feature, layer) {
  if (feature.properties && feature.properties.nombre) {
    layer.on("click", function (event) {
      if (feature.properties.nombre == _selectedDistrito) {
        if (_selectedLayer == LAYER_ALERTA) {
          analyzeColor(layer);
        } else if (_selectedLayer == LAYER_MORBILIDAD) {
          _layer_actual.eachLayer(function (layer) {
            analyzeColorMorbilidad(layer);
          });
        } else if (isProvinceOrCantonSelected()) {
          _layer_actual.eachLayer(function (layer) {
            layer.setStyle({ fillOpacity: 0.8 });
          });
        } else {
          layer.setStyle({ fillColor: COLOR_TRANSPARENT });
        }
        _selectedDistrito = null;
        if(_selectedProvince != null && _selectedCanton != null){
          changeGauge(_selectedProvince, _selectedCanton, null);
          $("#distritos").val("none");
        } else {
          $("#mapas").multiselect('enable');
        }
      } else {
        if(_selectedLayer != null && _selectedLayer.length > 0){
          toastr.warning("No se puede seleccionar un distrito si hay vistas en el mapa.", "Error");
          return;
        }
        if(_selectedProvince != null && (_selectedCanton == null || _selectedCanton == "NONE")){
          toastr.warning("Debe seleccionar un cantón para ver los detalles del distrito.", "Error");
          return;
        }
        else if(_selectedProvince != null && layer.options.fillColor != "rgba(255, 0, 0, 0.5)"){
          toastr.warning("No puede seleccionar este distrito porque no está dentro del cantón seleccionado.", "Error");
          return;
        }
        if (_selectedLayer == LAYER_ALERTA) {
          _layer_actual.eachLayer(function (layer) {
            analyzeColor(layer);
          });
          layer.setStyle({ fillColor: SELECTED_DISTRICT_COLOR });
        } else if (_selectedLayer == LAYER_MORBILIDAD) {
          _layer_actual.eachLayer(function (layer) {
            analyzeColorMorbilidad(layer);
          });
          layer.setStyle({ fillColor: SELECTED_DISTRICT_COLOR });
        } else if (isProvinceOrCantonSelected()) {
          _layer_actual.eachLayer(function (layer) {
            layer.setStyle({ fillOpacity: 0.3 });
          });
          layer.setStyle({ fillOpacity: 0.8 });
        } else {
          _layer_actual.eachLayer(function (layer) {
            layer.setStyle({ fillColor: COLOR_TRANSPARENT });
            _selectedDistrito = null;
          });
          layer.setStyle({ fillColor: SELECTED_DISTRICT_COLOR });
        }
        _selectedDistrito = feature.properties.nombre;
        if(_selectedProvince != null && _selectedProvince != "NONE" && _selectedCanton != null && _selectedCanton != "NONE"){
          changeGauge(_selectedProvince, _selectedCanton, _selectedDistrito);          
          $("#distritos").val(_selectedDistrito);
        }
        toastr.info("Distrito seleccionado: " + _selectedDistrito + ". Para deseleccionar, haga click en el distrito, o seleccione todas en provincia.", "Información");
        $("#mapas").multiselect('disable');
      }
      layer.setStyle({ color: DISTRICT_SELECT_STROKE });
      setDashboardData(feature);
    });

    layer.on("mouseover", function (event) {
      if (_selectedDistrito != null) {
        return false;
      }
      setDashboardData(feature);

      // weight: 0.3,
      layer.setStyle({ weight: 2, color: "blue" });
    });

    layer.on("mouseout", function (event) {
      layer.setStyle({ weight: 0.3, color: "red" });
    });
  }
}

function isProvinceOrCantonSelected() {
  return _selectedProvince != null || _selectedCanton != null;
}

function setDashboardData(feature) {
  $("#pro_info").html(
    (feature == null || feature.properties.proinfo == null ? "--" : feature.properties.proinfo)
  );
  $("#cant_info").html(
    (feature == null || feature.properties.cantinfo == null ? "--" : feature.properties.cantinfo)
  );
  $("#dis_info").html(
    (feature == null || feature.properties.nombre == null ? "--" : feature.properties.nombre)
  );
  $("#pobre_info").html(
    (feature == null || feature.properties.pobpobre == null ? "--" : feature.properties.pobpobre)
  );
  $("#pam_info").html(
    (feature == null || feature.properties.pobam == null ? "--" : feature.properties.pobam)
  );
  $("#pob_info").html(
    (feature == null || feature.properties.pobinfo == null ? "--" : feature.properties.pobinfo)
  );

  if($("#radio_sem0").is(":checked")){
    $("#cases-dashboard #activos .data").html(
      feature == null || feature.properties.activos == null ? "--" : feature.properties.activos
    );
    $("#cases-dashboard #recuperados .data").html(
      feature == null || feature.properties.recuperados == null ? "--" : feature.properties.recuperados
    );
    $("#cases-dashboard #fallecidos .data").html(
      feature == null || feature.properties.fallecidos == null ? "--" : feature.properties.fallecidos
    );
    $("#cases-dashboard #ataque .data").html(
      feature == null || feature.properties.ta == null ? "--" : feature.properties.ta
    );
    $("#cases-dashboard #r .data").html(
      feature == null || feature.properties.coef_var == null ? "--" : feature.properties.coef_var
    );
    $("#cases-dashboard #pendientes .data").html(
      feature == null || feature.properties.pendiente == null ? "--" : feature.properties.pendiente
    );
    $("#cases-dashboard #nuevos .data").html(
      feature == null || feature.properties.caso_dia == null ? "--" : feature.properties.caso_dia
    );
    $("#cases-dashboard2 #variacion .data").html(
      feature == null || feature.properties.coef_var == null ? "--" : feature.properties.coef_var + "%"
    );
    $("#socio").html(
      feature == null || feature.properties.socio == null ? "--" : feature.properties.socio
    );
    $("#den_info").html(
      feature == null || feature.properties.denuncias == null ? "--" : feature.properties.denuncias
    );
  } else {
    $("#cases-dashboard p.data:not(.pais)").html(
      "--"
    );

    $("#cases-dashboard #activos .data").html(
      _prediccionesMapa == null || _prediccionesMapa[feature.properties.codigo] == null || _prediccionesMapa[feature.properties.codigo].activos == null ? "--" : _prediccionesMapa[feature.properties.codigo].activos
    );

    $("#socio").html(
      _prediccionesMapa == null || _prediccionesMapa[feature.properties.codigo] == null || _prediccionesMapa[feature.properties.codigo].socio == null ? "--" : _prediccionesMapa[feature.properties.codigo].socio
    );
  }
}

function analyzeColor(layer) {
  if (layer.feature.properties.condicion !== undefined) {
    var condi = layer.feature.properties.condicion;
    if (condi == "Amarillo" || condi == "Amarilla") {
      layer.setStyle({ fillColor: "rgba(255, 255, 0, 0.8)", fillOpacity: 1 });
    } else if (condi == "Naranja") {
      layer.setStyle({ fillColor: "rgba(255, 165, 0, 0.8)", fillOpacity: 1 });
    } else {
      layer.setStyle({ fillColor: COLOR_TRANSPARENT });
    }
  } else {
    layer.setStyle({ fillColor: COLOR_TRANSPARENT });
  }
}

function analyzeColorSS(layer) {
  if (layer.feature.properties.socio !== undefined) {
    var condi = layer.feature.properties.socio;
    if (condi == "Muy baja") {
      layer.setStyle({ fillColor: "rgba(221,242,216, 0.4)", fillOpacity: 1 });
    } else if (condi == "Baja") {
      layer.setStyle({ fillColor: "rgba(114,199,199, 0.4)", fillOpacity: 1 });
    } else if (condi == "Media") {
      layer.setStyle({ fillColor: "rgba(67,167,204, 0.4)", fillOpacity: 1 });
    } else if (condi == "Alta") {
      layer.setStyle({ fillColor: "rgba(8,66,131, 0.4)", fillOpacity: 1 });
    }
  } else {
    layer.setStyle({ fillColor: COLOR_TRANSPARENT });
  }
}

function analyzeColorMorbilidad(layer) {
  if (layer.feature.properties.pobinfo !== undefined) {
    let poblacion = layer.feature.properties.pobinfo;
    switch(true){
      case poblacion <= 5000:
        layer.setStyle({ fillColor: "rgba(191,232,255, 1)", fillOpacity: 1 });
        break;
      case poblacion > 5000 && poblacion <= 10000:
        layer.setStyle({ fillColor: "rgba(0,198,255, 1)", fillOpacity: 1 });
        break;
      case poblacion > 10000 && poblacion <= 20000:
        layer.setStyle({ fillColor: "rgba(2,132,172, 1)", fillOpacity: 1 });
        break;
      case poblacion > 20000 && poblacion <= 40000:
        layer.setStyle({ fillColor: "rgba(0,94,227, 1)", fillOpacity: 1 });
        break;
      case poblacion > 40000:
        layer.setStyle({ fillColor: "rgba(0,5,1, 1)", fillOpacity: 1 });
        break;
    } 
  } else {
    layer.setStyle({ fillColor: "rgba(219, 228, 223, 0.4)" });
  }

  if(layer.feature.properties.morbilidad !== undefined){
    let morbilidad = layer.feature.properties.morbilidad;
    let factor = 1.0;
    let colorMorbilidad = "rgb(219, 228, 223)"; //Color gris, sin datos
    switch(true){
      case morbilidad < 15:
        colorMorbilidad = "rgb(217,217,217)";
        factor = 0.6;
        break;
      case morbilidad >= 15 && morbilidad <= 26:
        colorMorbilidad = "rgb(248,203,173)";
        factor = 0.8;
        break;
      case morbilidad >= 27 && morbilidad <= 37:
        colorMorbilidad = "rgb(221, 228, 4)";
        factor = 1.0
        break;
      case morbilidad >= 38 && morbilidad <= 51:
        colorMorbilidad = "rgb(228, 140, 2)";
        factor = 1.2;
        break;
      case morbilidad >= 52 && morbilidad <= 70:
        colorMorbilidad = "rgb(228, 86, 0)";
        factor = 1.4;
        break;
      case morbilidad > 71:
        colorMorbilidad = "rgb(228, 0, 0)";
        factor = 1.6;
        break;
    }
    if(layer.feature.properties.nombre != undefined && !_datosMorbilidad[layer.feature.properties.nombre]){
      var circulo = L.circle(layer.getBounds().getCenter(), {
        color: colorMorbilidad,
        fillColor: colorMorbilidad,
        fillOpacity: 1,
        radius: 250 * factor,
      }).addTo(circulosMorbilidad);
      circulo.bindTooltip("Distrito: " + layer.feature.properties.nombre + " Morbilidad: " + layer.feature.properties.morbilidad);
      _datosMorbilidad[layer.feature.properties.nombre] = true;
    }
  }
}

function ponerSedes(map) {
  var circle2 = L.circle([9.8826028, -84.0707764], {
    color: "red",
    fillColor: "#f03",
    fillOpacity: 0.5,
    radius: 500,
  }).addTo(map);


  var textLatLng = [9.8826028, -84.0707764];
  var myTextLabel = L.marker(textLatLng, {
    icon: L.divIcon({
      className: "text-labels", // Set class for CSS styling
      html: "CLUSTER",
    }),
    zIndexOffset: 1000, // Make appear above other map features
  }).addTo(map);

  let url = "get_json_sedes";
  $.get(url, function (result) {
    let datos_json = JSON.parse("[" + result["capas"] + "]");
    poner_sedes_mapa(map, datos_json);
  });

}


function ponerHogares(map) {
  let url = "get_json_hogares";
  $.get(url, function (result) {
    let datos_json = JSON.parse("[" + result["capas"] + "]");
    poner_hogares_mapa(map, datos_json);
  });
}


function ponerIndigenas(map) {
  let url = "get_json_indigenas";
  $.get(url, function (result) {
    let datos_json = JSON.parse("[" + result["capas"] + "]");
    poner_indigenas_mapa(map, datos_json);
  });
}

// function to get value from property "name" to populate for the popup
function onEachSede(feature, layer) {
  layer.bindPopup(feature.properties.nombre);
}

function onEachHogar(feature, layer) {
  layer.bindPopup(feature.properties.nombre);
}

function onEachIndigena(feature, layer) {
  layer.bindPopup(feature.properties.pueblo);
}

function poner_sedes_mapa(map, sedesJSON) {
  var myIcon = L.icon({
    iconUrl:
      "https://icons.iconarchive.com/icons/ampeross/qetto/16/icon-developer-icon.png",
    iconSize: [32, 37],
    iconAnchor: [16, 37],
    popupAnchor: [0, -28],
  });

  _layerSedes = L.geoJSON(null, {
    onEachFeature: onEachSede,
    pointToLayer: function (feature, latlng) {
      label = String(
        "<b>SEDE: </b>" +
          feature.properties.nombre +
          "<br/> <b>TOTAL:</b> " +
          feature.properties.total
      );
      return new L.CircleMarker(latlng, {
        radius: 4,
        color: "#016E00",
      }).bindTooltip(label, { permanent: false, opacity: 0.7 });
    },
  });

  if (_layerSedes != null) _layerSedes.addData(sedesJSON);
  map.addLayer(_layerSedes);
}

function poner_hogares_mapa(map, hogarJSON) {
  var myIcon = L.icon({
    iconUrl:
      "https://icons.iconarchive.com/icons/ampeross/qetto/16/icon-developer-icon.png",
    iconSize: [32, 37],
    iconAnchor: [16, 37],
    popupAnchor: [0, -28],
  });

  _layerHogares = L.geoJSON(null, {
    onEachFeature: onEachHogar,
    pointToLayer: function (feature, latlng) {
      label = String(
        "<b>HOGAR: </b>" +
          feature.properties.nombre 
      );
      return new L.CircleMarker(latlng, {
        radius: 3,
        color: "#bd9320",
      }).bindTooltip(label, { permanent: false, opacity: 0.7 });
    },
  });
 
  if (_layerHogares != null) _layerHogares.addData(hogarJSON);
  map.addLayer(_layerHogares);
}

function poner_indigenas_mapa(map, indigenaJSON) {
  var myIcon = L.icon({
    iconUrl:
      "https://icons.iconarchive.com/icons/ampeross/qetto/16/icon-developer-icon.png",
    iconSize: [32, 37],
    iconAnchor: [16, 37],
    popupAnchor: [0, -28],
  });

  var myStyle = {
    color: "#ff7800",
    opacity: 0.65,
  };
  
  _layerIndigenas = L.geoJSON(null, {
    style: myStyle,
    onEachFeature: function(feature, layer){
      label = "<b>PUEBLO: </b>" +
      feature.properties.pueblo;
      layer.bindTooltip(label);
    }
  }).addTo(map);

  if (_layerIndigenas != null) _layerIndigenas.addData(indigenaJSON);
	map.addLayer(_layerIndigenas);

}

/**
 * Configura las capas de proyecciones sobre el mapa según la fecha seleccionada y la cantidad de distritos de muestra en el select.
 * @param {*} muestra Cantidad de distritos muestreados para proyección: 15, 20, 40 o 50.
 */
function ponerProyecciones(muestra){
  let url = "getProyecciones";
  $.get(url, { fecha: _fechaActual, muestra: muestra }, function (result) {
    let proyecciones = result.proyecciones;
    let dist_actual;
    _layer_actual.eachLayer(function (layer) {
      dist_actual = layer.feature.properties.codigo.toString();
      if (proyecciones[dist_actual] !== undefined) {
        let color = "";
        switch(muestra){
          case 15:
            color = '#a8d18d';
            break;
          case 20:
            color = '#0d47a1';
            break;
          case 40:
            color = '#fea4a4';
            break;
          case 50:
            color = '#ff0000'
        }
        layer.setStyle({ fillColor: color });
        layer.setStyle({ fillOpacity: 0.5 });
        let label = "<b>Porcentaje: </b>" + proyecciones[dist_actual].porcentaje;
        layer.bindTooltip(label);
      }
    });
  });
}

function configurar_mapa(map, datos_json) {
  provincias = new L.FeatureGroup();
  if(_layer_actual != null){
    map.eachLayer(function(layer) {
      if (layer.toGeoJSON) {
        map.removeLayer(layer);
      }
    });
  }
  _layer_actual = new L.geoJSON(datos_json, {
    style: function (feature) {
      return {
        color: "red",
        weight: 0.3,
        opacity: 1,
        fillColor: "rgba(0, 255, 0,0)",
        fillOpacity: 1,
      };
    },
    onEachFeature: onEachFeature,
  }).addTo(provincias);
  map.addLayer(provincias);
  $.LoadingOverlay("hide");
}

window.onresize = function() {
  if (!window.matchMedia("(min-width: 1700px)").matches) {
    if(_wide_screen) {
      _wide_screen = false;
      window.location.reload();
    }
  } else {
    if(!_wide_screen){
      window.location.reload();
    }
  }
}

function setLayers(selectedLayers){
  let removedLayers = $(_selectedLayer).not(selectedLayers).get();
  if (removedLayers != null && removedLayers.length > 0)
    removeLayers(removedLayers);
  _selectedLayer = selectedLayers;
  // Si no hay valores seleccionados, _selectedLayer es null, poner capa clara por defecto
  if (_selectedLayer != null && _selectedLayer.length > 0) {
    $.each(_selectedLayer, function (index) {
      if (_selectedLayer[index] == LAYER_ALERTA) {
        // 3 Mostrar colores alerta
        _layer_actual.eachLayer(function (layer) {
          analyzeColor(layer);
        });
      }
      if (_selectedLayer[index] == LAYER_SS) {
        _layer_actual.eachLayer(function (layer) {
          analyzeColorSS(layer);
        });
      }

      if (_selectedLayer[index] == LAYER_MORBILIDAD) {
        circulosMorbilidad = L.featureGroup();
        _layer_actual.eachLayer(function (layer) {
          analyzeColorMorbilidad(layer);
        });
        if(_legend == null){
          map.addLayer(circulosMorbilidad);
          _legend = L.control({position: "bottomleft"});
          _legend.onAdd = function(map) {
            var div = L.DomUtil.create("div", "info legend");
            div.innerHTML +=
              '<img alt="legend" src=" /static/mapa/images/legend.png " width="145" height="225" />';
            return div;
          }
          _legend.addTo(map);
        }
      }
  
      if (_selectedLayer[index] == LAYER_SEDES && _layerSedes == null) { 
        ponerSedes(map);
      }
  
      if (_selectedLayer[index] == LAYER_PARADAS && _layerParadas == null) {
        cargarJSONParadas(map);
      }
  
      if (_selectedLayer[index] == LAYER_HOGARES && _layerHogares == null) {
        ponerHogares(map);
      }
      
      if (_selectedLayer[index] == LAYER_INDIGENAS && _layerIndigenas == null) { 
        ponerIndigenas(map);
      }

      if (_selectedLayer[index] == LAYER_FUENTES && _layerFuentes == null){
        cargarFuentesRadiactivas(map);
      }

      if (_selectedLayer[index] == LAYER_PROY_DIST_15){
        ponerProyecciones(15);
      }

      if (_selectedLayer[index] == LAYER_PROY_DIST_20){
        ponerProyecciones(20);
      }

      if (_selectedLayer[index] == LAYER_PROY_DIST_40){
        ponerProyecciones(40);
      }

      if (_selectedLayer[index] == LAYER_PROY_DIST_50){
        ponerProyecciones(50);
      }
  
    });
  } else {
    var pos = 0;
    L.tileLayer(urltile[pos], {
      attribution: contri,
      maxZoom: 18,
      accessToken:
        "XF87Xv2CrTh3C1C4ApZvDyWQTZoiSaVBGvmI0cG5tXJqXj5AVPxAQSSP20JXrjFw",
    }).addTo(map);
    _layer_actual.eachLayer(function (layer) {
      layer.setStyle({ fillColor: "rgba(0, 255, 0, 0)", fillOpacity: 1 });
    });
    if(map.hasLayer(circulosMorbilidad)){
      map.removeLayer(circulosMorbilidad);
      circulosMorbilidad = null;
      _datosMorbilidad = {};
      map.removeControl(_legend);
      _legend = null;
    }
  }
}

function initMap(){
  map = new L.map("my_map").setView([9.934739, -84.087502], 8);
  L.tileLayer(urltile[0], {
    attribution: contri,
    maxZoom: 18,
    accessToken:
      "XF87Xv2CrTh3C1C4ApZvDyWQTZoiSaVBGvmI0cG5tXJqXj5AVPxAQSSP20JXrjFw",
  }).addTo(map);

  L.control.scale().addTo(map);
}

function getDatosPais(){
  if(_fechaActual != null && _fechaActual != ""){
    let url = "getDatosPais";
    $.get(url, {fecha: _fechaActual}, function(result){
      $("#hccss .data").html(result.datos_pais.casos_salon);
      $("#ouci .data").html(result.datos_pais.casos_uci);
      $("#pms .data").html(result.datos_pais.indice_positividad);
    });
  }
}

function removeLayers(layers) {
  _layer_actual.eachLayer(function (layer) {
    layer.unbindTooltip();
  });
  if (layers.includes(LAYER_SEDES.toString()) && _layerSedes != null) {
    map.removeLayer(_layerSedes);
    _layerSedes = null;
  }
  if (layers.includes(LAYER_PARADAS.toString()) && _layerParadas != null) {
    map.removeLayer(_layerParadas);
    _layerParadas = null;
  }
  if (layers.includes(LAYER_HOGARES.toString()) && _layerHogares != null) {
    map.removeLayer(_layerHogares);
    _layerHogares = null;
  }
  if (layers.includes(LAYER_INDIGENAS.toString()) && _layerIndigenas != null) {
    map.removeLayer(_layerIndigenas);
    _layerIndigenas = null;
  }
  if (layers.includes(LAYER_FUENTES.toString()) && _layerFuentes != null) {
    map.removeLayer(_layerFuentes);
    _layerFuentes = null;
  }
}

/* Configuración para notificaciones de error. */
toastr.options.preventDuplicates = true;

/* Oculta el overlay de loading y muestra un mensaje de error si ocurre algún error en un request AJAX. */
$.ajaxSetup({
  error: function (xhr, status, error) {
    $.LoadingOverlay("hide");
    $("#gauge1").LoadingOverlay("hide");
    $("#Map").LoadingOverlay("hide");
    toastr.error("Ha ocurrido un error. Intente de nuevo más tarde. Error:" + error, "Error");
  },
});

/**
 * Cambia la fecha del mapa y recarga los datos desde la base de datos.
 * @param {*} date Fecha elegida para cargar los datos en el mapa.
 */
function setDate(date) {
  clearSelectList($("#cantones"), "none", "-- Seleccione provincia --");
  clearSelectList($("#distritos"), "none", "-- Seleccione cantón --");
  $("#provincias").val('none');
  $.LoadingOverlay("show");
  $.get("get_leaflet_dist", { date: date }, function (result) {
    let datos_json = JSON.parse("[" + result["capas"] + "]");
    configurar_mapa(map, datos_json);
    setDashboardData(null);
    _selectedProvince = null;
    _selectedCanton = null;
    _selectedDistrito = null;
    let tipoGrafico = $("input:radio[name=radio-group-1-bg]:checked").val();
    changeGauge(_selectedProvince, _selectedCanton, _selectedDistrito, (tipoGrafico == 'orden'? 1 : 2))
  });
}

/**
 * Solicita el mapa en SVG al servidor a través de una petición GET.
 * @param {string} url Url del método para cargar el mapa.
 */
function loadXMLMap(url) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      embedMap(this);
    }
  };
  xhttp.open("GET", url, true);
  xhttp.send();
  $.LoadingOverlay("show");
}

/**
 * Empotra el mapa cargado desde el servidor en el div correspondiente en la página.
 * @param {xml} xml Xml de respuesta del servidor que contiene el mapa en SVG.
 */
function embedMap(xml) {
  let xmlDoc = xml.responseText;
  let originalFill;

  /**Listener para capturar el evento de hover sobre los distritos del mapa.*/
  $(".svg-menu__path__seleccion__background *", "#col-mapa").hover(
    function () {
      if ($(this).attr("fill") == SELECTED_DISTRICT_COLOR) return;
      originalFill = $(this).attr("fill");
      $(this).attr("fill", "blue");

      if (_selectedDistrito == null) {
        let acumulados = $(this).attr("cantidad");
        let recuperados = $(this).attr("recuperados");
        let activos = $(this).attr("activos");
        let ta = $(this).attr("ta");
        let coef_var = $(this).attr("coef_var");
        let pendiente = $(this).attr("pendiente");
        let activos_prediccion = $(this).attr("activos_prediccion");

        let proInfo = $(this).attr("provincia");
        let cantInfo = $(this).attr("canton");
        let distInfo = $(this).attr("name_kml");

        $("#pro_info span").html(proInfo);
        $("#cant_info span").html(cantInfo);
        $("#dis_info").html(distInfo);

        $("#cases-dashboard #activos .data").html(activos);
        $("#cases-dashboard #recuperados .data").html(recuperados);
        $("#cases-dashboard #variacion .data").html(coef_var);
        $("#cases-dashboard #ataque .data").html(ta);
        $("#cases-dashboard #pendientes .data").html(pendiente);
      }
    },
    /** Se ejecuta al terminar la acción de hover. */
    function () {
      if ($(this).attr("fill") != SELECTED_DISTRICT_COLOR)
        $(this).attr("fill", originalFill);
      if (_selectedDistrito == null) $("#cases-dashboard .data").html("--");
    }
  );

  /** Listener para capturar el evento de click en un distrito, si hay cantón y provincia seleccionadas. */
  $(".svg-menu__path__seleccion__background *", "#col-mapa").on("click", function () {
      let distrito = $(this).attr("name_kml");
      seleccionarDistrito(distrito);
    }
  );
  ajaxRequestPlots();
}

function seleccionarDistrito(distrito){
  if (_selectedDistrito == distrito){
    return;
  }
      if (_selectedProvince != null && _selectedCanton != null) {
        let tempColor;
        if ($(this).attr("fill") != SELECTED_DISTRICT_COLOR) {
          tempColor = _originalDistrictColor;
          //_originalDistrictColor = originalFill;
          $(this).attr("fill", SELECTED_DISTRICT_COLOR);
        }
        if (_selectedDistrito != null) {
          let selectedProvinceClass = getClassSelector(_selectedProvince);
          let color = tempColor != null ? tempColor : originalFill;
          $(
            ".svg-menu__path__seleccion__background " +
              selectedProvinceClass +
              "[canton='" +
              _selectedCanton +
              "']" +
              "[name_kml='" +
              _selectedDistrito +
              "']",
            "#col-mapa"
          ).attr("fill", color);
        }
        _selectedDistrito = $(this).attr("name_kml");
        let recuperados = $(this).attr("recuperados");
        let activos = $(this).attr("activos");
        let proInfo = $(this).attr("provincia");
        let cantInfo = $(this).attr("canton");
        let distInfo = $(this).attr("name_kml");
        $("#pro_info").html(proInfo);
        $("#cant_info").html(cantInfo);
        $("#dis_info").html(distInfo);
        $("#cases-dashboard #activos .data").html(activos);
        $("#cases-dashboard #recuperados .data").html(recuperados);
      }
}

/**
 * Carga la biblioteca PanZoom para trabajar con el _apa después de que éste se haya cargado.
 */
function loadPanZoom() {
  _mapa = svgPanZoom("#my_map", {
    zoomEnabled: true,
    controlIconsEnabled: true,
    fit: true,
    center: true,
    contain: "inside",
  });
}

/**
 * Coloca un listener sobre el mapa para escalarlo al hacer resize de las columnas.
 */
function scaleMap() {
  let element = $("#pais");
  if (_resizer != null) ResizeSensor.detach(element);
  _resizer = new ResizeSensor(element, function () {
    scaleSVG(element.width());
  });
}

/**
 * Escala el mapa de forma proporcional al cambiar el tamaño del div que lo contiene.
 * @param {number} size Tamaño en pixeles que tendrá el mapa al recalcular su tamaño.
 */
function scaleSVG(size) {
  let svg = $("#pais svg");
  svg.css("width", size + "px");
  svg.css("height", size + "px");
  _mapa.resize();
  _mapa.updateBBox();
  _mapa.fit();
  _mapa.center();
}

/**
 * Obtiene el selector de clase de html para el valor del select elegido.
 * @param {string} selectedValue Valor del select list elegido.
 */
function getClassSelector(selectedValue) {
  if (selectedValue != null) {
    let classSelector;
    if (selectedValue.includes(" ")) {
      classSelector = "";
      let words = selectedValue.split(" ");
      for (let i = 0; i < words.length; ++i) {
        classSelector += "." + words[i];
      }
    } else {
      classSelector = "." + selectedValue;
    }
    return classSelector;
  } else {
    return null;
  }
}

/**
 * Cambia los valores del select de cantones al cambiar la provincia.
 * @param {*} province Provincia cuyos cantones serán cargados en el select.
 */
function changeCantones(province) {
  let url = "listarCantones";
  clearSelectList($("#cantones"), "none", "-- Todos --");
  $.get(url, { id: province }, function (result) {
    let options = "";
    for (let i = 0; i < result.cantones.length; ++i) {
      options +=
        '<option value="' +
        result.cantones[i] +
        '">' +
        result.cantones[i] +
        "</option>";
    }
    $("#cantones").append(options);
  });
}

/**
 * Cambia los valores del select de distritos al cambiar el cantón.
 * @param {*} canton Cantón cuyos distritos serán cargados en el select.
 */
function changeDistritos(canton) {
  let url = "listarDistritos";
  _selectedDistrito = null;
  clearSelectList($("#distritos"), "none", "-- Todos --");
  $.get(url, { id: canton }, function (result) {
    changeGauge(_selectedProvince, _selectedCanton, _selectedDistrito);
    let options = "";
    for (let i = 0; i < result.distritos.length; ++i) {
      options +=
        '<option value="' +
        result.distritos[i] +
        '">' +
        result.distritos[i] +
        "</option>";
    }
    $("#distritos").append(options);
  });
}

/**
 * Resalta la provincia seleccionada oscureciendo las demás del mapa.
 * @param {string} province Nombre de la provincia a resaltar en el mapa.
 */
function remarkSelectedProvince(province) {
  let selectedProvinceClass = getClassSelector(province);
  $("#pais path").css("opacity", PROVINCE_SELECT_OPACITY);
  $("#pais path").css("pointer-events", "none");
  $(selectedProvinceClass).css("opacity", "1");
  $(selectedProvinceClass).css("pointer-events", "auto");
}

/**
 * Elimina el resaltado de la provincia que había seleccionada.
 */
function unmarkSelectedProvince() {
  $("#pais path").css("opacity", "1");
  $("#pais path").css("pointer-events", "auto");
}

/**
 * Resalta el cantón seleccionado oscureciendo los demás de la provincia, en menor medida que la opacidad de las demás provincias
 * para que resalte, además de colocar un borde de color rojo y más grueso para este efecto.
 * @param {string} canton Nombre del cantón a resaltar en la provincia seleccionada.
 */
function remarkSelectedCanton(canton) {
  let selectedProvinceClass = getClassSelector(_selectedProvince);
  $(selectedProvinceClass).css("opacity", CANTON_SELECT_OPACITY);
  $(selectedProvinceClass).css("pointer-events", "none");
  let distritos = $(selectedProvinceClass + '[canton="' + canton + '"]');
  $('path[canton="' + canton + '"]').css("stroke", DISTRICT_SELECT_STROKE);
  $('path[canton="' + canton + '"]').css(
    "stroke-width",
    DISTRICT_SELECTED_STROKE_WIDTH
  );
  distritos.css("opacity", "1");
  distritos.css("pointer-events", "auto");
}

/**
 * Elimina el resaltado del cantón que había sido seleccionado.
 */
function unmarkSelectedCanton(canton = _selectedCanton) {
  if (canton != null) {
    let selectedProvinceClass = getClassSelector(_selectedProvince);
    $(selectedProvinceClass).css("opacity", "1");
    $(selectedProvinceClass).css("pointer-events", "auto");
    let distritos = $(selectedProvinceClass + '[canton="' + canton + '"]');
    distritos.css("stroke", DISTRICT_DEFAULT_STROKE);
    distritos.css("stroke-width", DISTRICT_DEFAULT_STROKE_WIDTH);
  }
}

/**
 * Limpia un select list que depende del select de provincia.
 * @param {string} selector Selector css del select list a limpiar.
 * @param {*} defaultOptionValue Valor de la opcion por defecto del select list.
 * @param {*} defaultOptionText Texto de la opción por defecto del select list.
 */
function clearSelectList(selector, defaultOptionValue, defaultOptionText) {
  selector.html(
    '<option value="' +
      defaultOptionValue +
      '" >' +
      defaultOptionText +
      "</option>"
  );
}

/**
 * Actualiza el gauge con la información de la provincia
 * @param provincia Provincia cuyos datos serán cargados en el gráfico de líneas.
 */
function changeGauge(province = null, canton = null, distrito = null, tipo = ($("input:radio[name=radio-group-1-bg]:checked").val() == 'orden'? 1 : 2)) {
  
  let url = tipo == 1 ? "getGaugeChart" : "getVacunas";
  $("#gauge1").LoadingOverlay("show");
  $("#Map").LoadingOverlay("show");
  $.get(
    url,
    { province: province, canton: canton, distrito: distrito, fecha: _fechaActual },
    function (result) {
      $("#gauge1").html(result["chart"]);
      $("#gauge1").LoadingOverlay("hide");
      $("#Map").LoadingOverlay("hide");
      if(tipo != 1){
        $("#fuente-vac").removeClass("d-none");
        $("#fuente-vac").addClass("d-block");
      } else {
        $("#fuente-vac").removeClass("d-block");
        $("#fuente-vac").addClass("d-none ");
      }
    }
  );
}

/**
 * Configura los bubbles con los créditos de los colaboradores.
 */
function setUpCreditsBubbles() {
  $("#ucr-credits").bubble();
}

/**
 * Restaura el color de un distrito seleccionado al que tenía originalmente en el mapa.
 */
function restoreColor() {
  if (_selectedDistrito != null) {
    let selectedProvinceClass = getClassSelector(_selectedProvince);
    $(
      ".svg-menu__path__seleccion__background " +
        selectedProvinceClass +
        "[canton='" +
        _selectedCanton +
        "']" +
        "[name_kml='" +
        _selectedDistrito +
        "']",
      "#col-mapa"
    ).attr("fill", _originalDistrictColor);
    _originalDistrictColor = null;
  }
}

/**
 * Solicita al servidor ciertos gráficos para insertarlos en la página luego de haberse cargado, para aligerar el tiempo de carga inicial y hacer que los gráficos se ajusten bien a los divs padres.
 */
function ajaxRequestPlots() {
  let url = "getPlots";
  $("#col-indicadores").LoadingOverlay("show");
  $.get(url, function (result) {
    $("#grafico2").html(result["plot2"]);
    $("#graficoVacunas").html(result["graficoVacunas"]);
    // $("#grafico3").html(result["plot8"]);
    // $("#grafico4").html(result["plot9"]);
    // $("#grafico5").html(result["plot10"]);
    // $("#grafico6").html(result["plot11"]);
    $("#col-indicadores").LoadingOverlay("hide");
  });
}

function parseDate(date){
  let newDate = "";
  let dateParts = date.split('-');
  newDate = dateParts[2] + '/' + dateParts[1] + '/' + dateParts[0];
  return newDate;
}