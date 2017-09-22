$(document).ready(function()
    {
        $("#table").tablesorter({textExtraction: "complex", dateFormat:"dd.mm.yyyy", widgets:['zebra'], headers: {1:{sorter:'eudate'}}});
    }
);