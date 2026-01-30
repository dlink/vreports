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
function reset_page_num() {
    document.form1.page_num.value = 1;
}

/* sort controls */
function set_sort(column_name, direction) {
    let form = document.form1;
    let current = form.sort_by.value || '';
    let [cur_col, cur_dir] = current.split(':');

    if (column_name != cur_col) {
	form.sort_by4.value = form.sort_by3.value
	form.sort_by3.value = form.sort_by2.value;
	form.sort_by2.value = form.sort_by.value;
    }
    form.sort_by.value = column_name + ':' + direction
    form.submit();
    return true;
}

function set_s_sort(column_name, direction) {
    let form = document.form1;
    let current = form.s_sort_by.value || '';
    let [cur_col, cur_dir] = current.split(':');

    if (column_name != cur_col) {
	form.s_sort_by4.value = form.s_sort_by3.value
	form.s_sort_by3.value = form.s_sort_by2.value;
	form.s_sort_by2.value = form.s_sort_by.value;
    }
    form.s_sort_by.value = column_name + ':' + direction
    form.submit();
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
	  reset_page_num();
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

/** Apply Excel-like conditional format on percent values, 
 **  >= 0 Green
 **  < 0 Red
 **  Works on .vtable td.vpercent
 */
$(function() {
  const tables = document.getElementsByClassName("vtable");

  for (let table of tables) {
    const percentageCells = table.getElementsByClassName("shade_percent");

    for (let cell of percentageCells) {
      // Skip header cells and empty fields
      if (cell.tagName === "TH" || cell.textContent.trim() === "") {
        continue;
      }

      const percentage = parseFloat(cell.textContent);

      // Apply even more subtle colors
      if (percentage < 0) {
          cell.style.backgroundColor = "#ffe6e6"; // Very light red
      } else {
          cell.style.backgroundColor = "#e6ffe6"; // Very light green
      }
    }
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

document.querySelectorAll('#customize-report-panel input, #customize-report-panel select, #customize-report-panel textarea')
  .forEach(function(el) {
    el.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault(); // optional
        const form = el.closest('form');
        if (form) form.submit();
      }
    });
  });

// Multi-select
$(document).ready(function() {
    $('.multiple_select').select2({
	width: '100%',
	closeOnSelect: false
    });
});
