$('.box.thumb').click(function(e){
    if ($(e.target).is('a') ||
        $(e.target).parent().is('a') ||
        $(e.target).hasClass('ficon-close') ||
        $(e.target).hasClass('call-to-action') ||
        $(e.target).parents('.call-to-action').length > 0) {
            return;
    }
    $('.box-preview:visible .ficon-close').trigger('click');
    box_preview($(e.target).parents('.box'));
});

function box_preview(box) {
    var b = box.find('.box-preview');
    if ( b.is(':visible') ) {
        b.hide(400);
    } else {
        $('.box-preview').hide();
        b.show(400);
    }
}

function close_preview(el) {
    var box_preview = el.parents('.box-preview');
    $('.box-preview').hide(400, function() {
        box_preview.find('iframe').remove().appendTo(box_preview.find('.box-video'));
    });
}

function filterBoxes(filter, el) {
    $('#main-side-nav .item.active').removeClass('active');
    $(el).addClass('active');
    var filterSelector = "";
    if (filter != "") {
        filterSelector = '.'+filter;
    }
    if ($('.box.thumb:visible').length == 0) {
        $('.box.thumb'+filterSelector).fadeIn('fast');
    } else {
        $('.box.thumb:visible').fadeOut('fast', function() {
            $('.box.thumb'+filterSelector).fadeIn('fast');
        });
    }
}


var last_box_id = '';
function leave_box(el,id) {
    last_box_id = id;
    $(el).parents('.box.thumb').fadeOut();
    ajaxPost(
        '/box/leave/',
        {'box_id': id},
        function(response) {
            $(el).parents('.box.thumb').remove();
        },
        {
            'onError': function(response){
                $(el).parents('.box.thumb').stop(true,true).fadeIn();
            }
        }
    );
}