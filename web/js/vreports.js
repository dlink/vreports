function open_left_nav() {
    $('#left-nav').show('slow');
    $('#left-nav-open').hide('slow');
}
function close_left_nav() {
    $('#left-nav').hide('slow');
    $('#left-nav-open').show('slow');
}
function reset_filters() {
    $('#filter-chooser input[type=text]').val('');
    $('#filter-chooser input[type=checkbox]').attr('checked', false);
    $('#filter-chooser select').val(0);
    return true;
}
function reset_summaries() {
    $('#summary-chooser select').val('');
}
function reset_columns() {
    $('#column-chooser :checkbox').prop('checked', false);
    $('#column-chooser .default_column').prop('checked', true);
    return true;
}
function clear_columns() {
    $('#column-chooser :checkbox').prop('checked', false);
    return true;
}

/* paging controls */
function go_to_prev_page() {
    document.form1.page_num.value = parseInt(document.form1.page_num.value)-1;
    document.form1.submit(); 
    return true;
}
function go_to_next_page() {
    document.form1.page_num.value = parseInt(document.form1.page_num.value)+1;
    document.form1.submit(); 
    return true;
}

/* sort controls */
function set_sort(column_name, direction) {
    document.form1.sort_by.value = column_name + ':' + direction
    document.form1.submit();
    return true;
}
function set_s_sort(column_name, direction) {
    document.form1.s_sort_by.value = column_name + ':' + direction
    document.form1.submit();
    return true;
}

$(function() {
   $(".date").datepicker({dateFormat: "yy-mm-dd" });

   // Fix form action if current page contains GET parameters
   if(window.location.href.indexOf('?') != -1) {
     var cleanUrl = window.location.href.substring(0, window.location.href.indexOf('?'));
     $("form[name=form1]")
       .attr('action', cleanUrl)
       .attr('method', 'POST');
   }

   /* Show Customize Report Panel Window */
   var b = document.getElementById('customize-report-button');
   if (b) {
      b.addEventListener('click', function() {
          var m = document.getElementById('customize-report-panel-wrapper');
          if (m) {
              toggleClass(m, 'show');
          }
      });
  }

  /* Show SQL Panel */
  var b = document.getElementById('show-sql-button');
  if (b) {
      b.addEventListener('click', function() {
         var m = document.getElementById('sql_panel');
         if (m) {
	     toggleClass(m, 'show');
         }
      });
  }

  /* submit customizations */
  var b = document.getElementById('customize-report-submit-button');
  if (b) {
      b.addEventListener('click', function() {
          var m = document.getElementById('customize-report-panel-wrapper');
	  if (m) {
	      toggleClass(m, 'show');
	  }
	  var p = document.getElementById('loading-indicator-wrapper');
	  if (p) {
              toggleClass(p, 'show');
	  }
	  document.form1.submit();
      });
  }

  /* close customizations */
  var b = document.getElementById('close');
  if (b) {
      b.addEventListener('click', function() {
          var m = document.getElementById('customize-report-panel-wrapper');
	  if (m) {
	      toggleClass(m, 'show');
	  }
	  });
  }

  /* cancel customizations */
  var b = document.getElementById('customize-report-cancel-button');
  if (b) {
      b.addEventListener('click', function() {
          var m = document.getElementById('customize-report-panel-wrapper');
	  if (m) {
	      toggleClass(m, 'show');
	  }
      });
  }
});

/** toggleClass
 ** Toggles supplied className on element.
 */
function toggleClass(element, elemClass){
  "use strict";
  if (!element || !elemClass){
      return false;
  }
  if (typeof element.className !== 'undefined') {
    var index = 0, found = false, classes = element.className.split(' ');
    for (var i = 0, len = classes.length; !found && i < len; i++) {
      if (classes[i] === elemClass) {
        index = i;
        found = true;
      }
    }
    if (!found) {
      classes.push(elemClass);
    }
    else {
      classes.splice(index, 1);
    }
    element.className = classes.join(' ');
  }
  return true;
}
