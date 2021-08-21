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
const URL_SCRIPT_PARADAS = '/static/js/paradas.js';
const URL_SCRIPT_FUENTES_RADIACTIVAS = '/static/js/fuentesRadiactivas.js';

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
var _paradasCargadas = false;
var _fuentesRadiactivasCargadas = false;

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
  "preventDuplicates": true,
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

/* Oculta el overlay de loading y muestra un mensaje de error si ocurre algún error en un request AJAX. */
$.ajaxSetup({
  error: function (xhr, status, error) {
    $.LoadingOverlay("hide");
    $("#gauge1").LoadingOverlay("hide");
    $("#Map").LoadingOverlay("hide");
    toastr.error("Ha ocurrido un error. Intente de nuevo más tarde. Error: " + status, "Error");
  },
});

/**INICIALIZADOR**/
/**
 * Realiza todas las peticiones necesarias para el cargado inicial de datos en la vista.
 * - Configura las columnas ajustables en pantalla ancha.
 * - Inicializa el mapa.
 * - Inicializa el calendario con las fechas apropiadas.
 * - Inicializa los event listeners.
 * - Inicializa el indicador de fecha y hora actual.
 * - Inicializa los gráficos.
 * - Inicializa las burbujas de créditos.
 */
window.onload = function () {
  $.noConflict();

  initColumns();

  initMap();

  initDates();

  getDatosPais();

  setUpListeners();
  
  setInterval(timerDaemon, 1000);  

  ajaxRequestPlots();

  setUpCreditsBubbles();
};

/**
 * Configura las columnas ajustables, solo si el ancho del viewport es de 1700px o mayor.
 * De lo contrario, la vista se muestra en filas en vez de columnas.
 */
function initColumns(){
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
}

/**
 * Inicializa el calendario con las fechas válidas y carga las capas del mapa con la fecha más actualizada de los datos.
 */
function initDates(){
  $.get("getValidDates", function(result){
    _fechasValidas = result.fechas;
    $.get("getUltimaFecha", function(result){
      _ultimaFecha = result.date[0];
      _fechaActual = _ultimaFecha;
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
          minDate: "06/03/2020", // Fecha del primer caso reportado en C.R.
          maxDate: parseDate(_ultimaFecha),
        },
        function (start, end, label) {
          _fechaActual = start.format("YYYY-MM-DD");
          setDate(_fechaActual);
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
      
      setDate(_ultimaFecha);
    });
  });
}

/**
 * Configura los event listeners de resize(window), los selects, radio buttons y multiselect.
 */
function setUpListeners(){

  /* Listener sobre el evento de resize de la ventana, para que la página sea responsive dinámicamente. */
  $(window).resize(function(){
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
    buttonContainer: '<div class="" />',
    buttonClass: "form-control",
    nonSelectedText: "Seleccione",
    allSelectedText: "Todas",
    selectAllText: "Todas",
    nSelectedText: "seleccionadas",
    numberDisplayed: 1,
  });
  
  //  Colorea de azul la provincia seleccionada en el select.
  //  Baja la opacidad de las demás provincias para resaltar la seleccionada.
  //  Limpia los datos de variables globales cuando ya no se van a usar.
   
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
    changeGauge(_selectedProvince, _selectedCanton, selectedDistrito);
  });

  $("input[data-provide=datepicker]").on("click", function () {
    $(".datepicker.datepicker-dropdown").css("z-index", "1000");
  });
}

/** 
 * Coloca la fecha en el formato DD/MM/YYYY HH:MM:SS.
 */
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

/**
 * Obtiene las predicciones para todos los cantones en una semana dada, en el mes de la fecha seleccionada en el datepicker,
 * y guarda los datos en un JSON en una variable global.
 * @param {string} semana Semana de predicciones: I, II, III, IV, o V.
 */
function getPredicciones(semana){
  let mes = parseInt($("[name='datepicker']").val().split('/')[1]);
  let url = 'getPrediccionesMapa';
  $.get(url, {mes: mes, semana: semana}, function(result){
    _prediccionesMapa = result.predicciones;
  });
}

/**
 * Configura la apariencia, metadatos y acciones (event listeners) para la capa de distritos del mapa.
 * @param {*} feature Objeto de metadatos para cada distrito. Contiene el nombre y todos los datos epidemiológicos obtenidos de
 * la base de datos para cada distrito.
 * @param {*} layer Capa correspondiente a cada distrito, asociada a los metadatos (features).
 */
function onEachFeature(feature, layer) {
  if (feature.properties && feature.properties.nombre) {
    layer.on("click", function (event) {
      if (feature.properties.nombre == _selectedDistrito) {
        if (isProvinceOrCantonSelected()) {
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
        if (isProvinceOrCantonSelected()) {
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

      layer.setStyle({ weight: 2, color: "blue" });
    });

    layer.on("mouseout", function (event) {
      layer.setStyle({ weight: 0.3, color: "red" });
    });
  }
}

/**
 * Verifica si existe un cantón o provincia seleccionados en el mapa (a través de los combo boxes).
 * @returns True si existe un cantón o provincia seleccionados, false en caso contrario.
 */
function isProvinceOrCantonSelected() {
  return _selectedProvince != null || _selectedCanton != null;
}

/**
 * Establece los datos del dashboard a partir de los metadatos del feature que se pasa por parámetro.
 * Coloca placeholders '--' en las casillas si el feature es nulo.
 * @param {*} feature Objeto de features que contiene los metadatos de la capa asociada (distrito).
 */
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

/**
 * Configura los colores de los distritos según el nivel de alerta.
 * @param {*} layer Layer sobre la cual se colocará el color del distrito de acuerdo al nivel de alerta.
 */
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

/**
 * Configura los colores de los distritos según el índice socio sanitario.
 * @param {*} layer Layer sobre la cual se colocará el color del distrito de acuerdo al índice socio sanitario.
 */
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

/**
 * Configura los colores de los distritos según los datos de morbilidad.
 * @param {*} layer Layer sobre la cual se colocará el color del distrito de acuerdo a los datos de morbilidad.
 */
function analyzeColorMorbilidad(layer) {
  
  // Configura el color de fondo de los distritos de acuerdo a la cantidad de habitantes.
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

  // Configura el color y tamaño de los círculos que indican la tasa de morbilidad por distrito.
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
    // Coloca los círculos de tasa de morbilidad en el centro geográfico de los distritos.
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

/**
 * Obtiene la capa de sedes de la base de datos y la coloca como una nueva capa sobre el mapa.
 * @param {*} map Mapa sobre el que se colocará la nueva capa de sedes.
 */
function ponerSedes(map) {
  let url = "get_json_sedes";
  $.get(url, function (result) {
    let sedesJSON = JSON.parse("[" + result["capas"] + "]");
    _layerSedes = L.geoJSON(null, {
      onEachFeature: function(feature, layer){
        layer.bindPopup(feature.properties.nombre);
      },
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
  });
}

/**
 * Obtiene la capa de hogares de ancianos de la base de datos y la coloca como una nueva capa sobre el mapa.
 * @param {*} map Mapa sobre el que se colocará la nueva capa de hogares de ancianos.
 */
function ponerHogares(map) {
  let url = "get_json_hogares";
  $.get(url, function (result) {
    let hogarJSON = JSON.parse("[" + result["capas"] + "]");
    _layerHogares = L.geoJSON(null, {
      onEachFeature: function(feature, layer){
        layer.bindPopup(feature.properties.nombre);
      },
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
  });
}

/**
 * Obtiene la capa de asentamientos indígenas de la base de datos y la coloca como una nueva capa sobre el mapa.
 * @param {*} map Mapa sobre el que se colocará la nueva capa de asentamientos indígenas.
 */
function ponerIndigenas(map) {
  let url = "get_json_indigenas";
  $.get(url, function (result) {
    let indigenaJSON = JSON.parse("[" + result["capas"] + "]");
    _layerIndigenas = L.geoJSON(null, {
      style: {
        color: "#ff7800",
        opacity: 0.65,
      },
      onEachFeature: function(feature, layer){
        label = "<b>PUEBLO: </b>" +
        feature.properties.pueblo;
        layer.bindTooltip(label);
      }
    }).addTo(map);
  
    if (_layerIndigenas != null) _layerIndigenas.addData(indigenaJSON);
    map.addLayer(_layerIndigenas);
  });
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

/**
 * Configura las capas iniciales del mapa al cargar la página.
 * @param {*} map Objeto del mapa donde se colocarán las capas.
 * @param {*} datos_json Capas en formato JSON a ser colocadas en el mapa.
 */
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

/**
 * Agrega o quita capas del mapa, según la selección de capas que se realice en el multiselect de capas.
 * @param {*} selectedLayers Lista de capas seleccionadas en el multiselect de capas.
 */
function setLayers(selectedLayers){
  // Obtiene las capas no seleccionadas y las elimina.
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
  
      // Carga dinámicamente el script que contiene las paradas en formato GeoJSON, para acelerar la carga inicial de la página.
      if (_selectedLayer[index] == LAYER_PARADAS && _layerParadas == null) {
        if(_paradasCargadas){
          cargarJSONParadas(map);
        } else {
          $.getScript(URL_SCRIPT_PARADAS, function(){
            cargarJSONParadas(map);
          });
        }
      }
  
      if (_selectedLayer[index] == LAYER_HOGARES && _layerHogares == null) {
        ponerHogares(map);
      }
      
      if (_selectedLayer[index] == LAYER_INDIGENAS && _layerIndigenas == null) { 
        ponerIndigenas(map);
      }

      // Carga dinámicamente el script que contiene las fuentes radiactivas en formato GeoJSON, para acelerar la carga inicial de la página.
      if (_selectedLayer[index] == LAYER_FUENTES && _layerFuentes == null){
        if(_fuentesRadiactivasCargadas){
          cargarFuentesRadiactivas(map);
        } else {
          $.getScript(URL_SCRIPT_FUENTES_RADIACTIVAS, function(){
            cargarFuentesRadiactivas(map);
          });
        }
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
    // Coloca el color por defecto en todos los distritos si no hay capas seleccionadas.
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

/**
 * Quita capas específicas del mapa.
 * @param {*} layers Capas no seleccionadas en el multiselect del mapa.
 */
function removeLayers(layers) {
  // Quita todos los tooltips
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

/**
 * Inicializa la vista por defecto del mapa, centrado sobre Costa Rica.
 */
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

/**
 * Obtiene los datos a nivel país (Índice de positivdad, hospitalizaciones (salón) y hospitalizaciones (UCI) de la CCSS), en la fecha seleccionada,
 * y los coloca en el dashboard de datos país.
 */
function getDatosPais(){
  let url = "getDatosPais";
  $.get(url, {fecha: _fechaActual}, function(result){
    $("#hccss .data").html(result.datos_pais.casos_salon);
    $("#ouci .data").html(result.datos_pais.casos_uci);
    $("#pms .data").html(result.datos_pais.indice_positividad);
  });
}

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
    getDatosPais();
  });
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
 * Solicita al servidor ciertos gráficos para insertarlos en la página luego de haberse cargado, para aligerar el tiempo de carga inicial y hacer que los gráficos se ajusten bien a los divs padres.
 */
function ajaxRequestPlots() {
  let url = "getPlots";
  $("#col-indicadores").LoadingOverlay("show");
  $.get(url, function (result) {
    $("#grafico2").html(result["plot2"]);
    $("#graficoVacunas").html(result["graficoVacunas"]);
    $("#col-indicadores").LoadingOverlay("hide");
  });
}

/**
 * Cambia la fecha del formato ISO (YYYY-MM-DD) a formato español con / (DD/MM/YYYY).
 * @param {*} date Fecha en formato ISO
 * @returns Fecha en español en formato DD/MM/YYYY. 
 */
function parseDate(date){
  let newDate = "";
  let dateParts = date.split('-');
  newDate = dateParts[2] + '/' + dateParts[1] + '/' + dateParts[0];
  return newDate;
}