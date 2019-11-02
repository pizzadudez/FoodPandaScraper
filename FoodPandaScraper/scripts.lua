function main(splash)
    assert(splash:go(splash.args.url))
    splash:wait(5)

    local get_element_dim_by_xpath = splash:jsfunc([[
        function(xpath) {
            var element = document.evaluate(xpath, document, null,
                XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            var element_rect = element.getClientRects()[0];
            return { "x": element_rect.left, "y": element_rect.top }
        }
    ]])
    menu_item = get_element_dim_by_xpath('/html/body/div[13]/div[1]/main/div[2]/section/div[2]/div/div/div[3]/section/div[1]/ul[1]/li[2]/div')
    splash:set_viewport_full()
    splash:mouse_click(menu_item.x, menu_item.y)
    splash:wait(5)

    return splash:html()
end