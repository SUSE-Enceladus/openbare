// Copyright © 2016 SUSE LLC.
//
// This file is part of openbare.
//
// openbare is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// openbare is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with openbare. If not, see <http://www.gnu.org/licenses/>.

function toggleLendableChoices(value, duration) {
    /*
    * Toggle the lendable choices select widget. If haslendable
    * option of mail to choices is selected, lendable select is
    * visible and required.
    */

    if(value === "haslendable") {
        $("#id_lendable").show(duration);
    }
    else {
        $("#id_lendable").hide(duration);
    }
}

$(document).ready(function() {
    var toChoice = document.getElementById("id_to");

    // Add toggle function to mail to choice select widget.
    toChoice.addEventListener("change", function() {
        toggleLendableChoices(toChoice.value, 100);
    });

    // Toggle lendable choices with no transition on page load.
    toggleLendableChoices(toChoice.value, 0);

    // When send mail clicked from modal submit form.
    $("#id_send_mail_btn").click(function() {
        $("#id_mail_form").submit();
    });
});
