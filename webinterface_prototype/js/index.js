function checkbox_constraint(this_checkbox) {
  this_checkbox_checked = document.getElementById(this_checkbox).checked;
  if (this_checkbox_checked) {
    if (this_checkbox == "checkbox_noun") {
      document.getElementById("checkbox_verb").disabled = true;
      document.getElementById("checkbox_noun").checked = true;
    }
    else if (this_checkbox == "checkbox_verb") {
      document.getElementById("checkbox_noun").disabled = true;
      document.getElementById("checkbox_verb").checked = true;
    }
  }
  else {
    if (this_checkbox == "checkbox_noun") {
      document.getElementById("checkbox_verb").disabled = false;
      document.getElementById("checkbox_noun").checked = false;
    }
    else if (this_checkbox == "checkbox_verb") {
      document.getElementById("checkbox_noun").disabled = false;
      document.getElementById("checkbox_verb").checked = false;
    }
  }
}
