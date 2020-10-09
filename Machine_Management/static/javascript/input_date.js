

$("input[type=date]").change(function () {
    this.setAttribute("value",moment(this.value, "").format("DD/MM/YYYY"));
});

$("input[type=date]").show(function () {
    if (this.value == ""){
        this.value = moment().format("YYYY-MM-DD");
    }
    var date = this.value;
    this.setAttribute("value",moment(this.value).format("DD/MM/YYYY"));
    this.value = date;
});
