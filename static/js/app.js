// FUNCTIONALITY FOR PLUS - MINUS BUTTON IN FAQ PAGE
$(".signIcon").click(function() {
    var current_state = $(this).parent().parent().children("p").css("display");
    if (current_state == "none") {
        $(this).parent().parent().children("p").css("display", "block");
        $(this).parent().parent().children("form").css("display", "flex");
        $(this).parent().parent().children("h5").children("span").text("-");
    }
    else {
        $(this).parent().parent().children("p").css("display", "none");
        $(this).parent().parent().children("form").css("display", "none");
        $(this).parent().parent().children("h5").children("span").text("+");
    }
})

$("#addQuestionButton").click(function() {
    var current_display = $(".addAsk").css("display");
    if (current_display == "none") {
        $(".addAsk").css("display", "block");
    }
    else {
        $(".addAsk").css("display", "none");
    }
})

$(".cancelButton").click(function() {
    $(".addAsk").css("display", "none");
})


// FUNCTIONALITY FOR EYE BUTTON IN LOGIN PAGE
$(".watchButton").click(function() {
    var current_html = $(this).children("i").attr("class");
    if (current_html.includes("slash")) {
        $(this).html("<i class='bi bi-eye-fill'></i>");
        $("#loginPassword").attr("type", "text");
    }
    else {
        $(this).html("<i class='bi bi-eye-slash-fill'></i>");
        $("#loginPassword").attr("type", "password");
    }
})


// FUNCTIONALITY FOR EYE BUTTON IN REGISTRATION PAGE
$(".watchRegisterButton").click(function() {
    var current_html = $(this).children("i").attr("class");
    if (current_html.includes("slash")) {
        $(this).html("<i class='bi bi-eye-fill'></i>");
        $("#loginPassword").attr("type", "text");
    }
    else {
        $(this).html("<i class='bi bi-eye-slash-fill'></i>");
        $("#loginPassword").attr("type", "password");
    }
})

// FUNCTIONALITY FOR APPLY BUTTON IN EACH JOB PAGE
$(".applyButton").click(function() {
    $(".jobFillForm").toggleClass("jobFormHelper");
})

$(".jobCancelButton").click(function() {
    $(".jobFillForm").toggleClass("jobFormHelper");
})

// FUNCTIONALITY FOR TEXTAREA INPUT IN EDIT PAGE:
if ($("#textId").val() != null) {
    var hiddenInput = $("#textId").val();
    if (hiddenInput.length > 0) {
        $(".editTextArea1").val(hiddenInput);
    }
}

// FUNCTIONALITY FOR PROVIDER PAGE
if ($(".chosenProviderName").first().text() != null) {
    var chosenProviderName = $(".chosenProviderName").first().text()
    if (chosenProviderName.length > 0) {
        $(".myChosenProvider").text(chosenProviderName);
    }
}

// FUNCTIONALITY - DISABLE RESUBMISSION
if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}