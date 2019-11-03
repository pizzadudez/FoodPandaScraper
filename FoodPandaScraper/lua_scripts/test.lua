function main(splash)
    splash.private_mode_enabled = false
    assert(splash:go(splash.args.url))
    assert(splash:wait(3))

    local get_element_dim_by_xpath = splash:jsfunc([[
        function(xpath) {
            var element = document.evaluate(xpath, document, null,
                XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            var element_rect = element.getClientRects()[0];
            return { "x": element_rect.left, "y": element_rect.top }
        }
    ]])
    local get_element_dim = splash:jsfunc([[
        function(el) {
            var el_rect = el.getClientRects()[0];
            return { "x": el_rect.left, "y": el_rect.top }
        }
    ]])
  
    local enter_adress = get_element_dim_by_xpath('/html/body/div[13]/div[1]/main/div[2]/section/div[1]/div[1]/div[2]/form/div[1]/div/input')
    splash:set_viewport_full()
    splash:mouse_click(enter_adress.x, enter_adress.y)
    splash:send_text('Strada Morii 25, Brașov 500063, România')
    splash:wait(2)

    local verify_adress = get_element_dim_by_xpath('//*[@id="delivery-information-postal-index-form"]/div[2]/button[1]')
    splash:set_viewport_full()
    splash:mouse_click(verify_adress.x, verify_adress.y)
    splash:wait(2)
        
    local response_list = {}

    local selector = '.dish-card.h-product.menu__item'
    local menu_items = splash:select_all(selector)

    for i, item in pairs(menu_items) do
        local has_topping = item.node:getAttribute("data-has-priced-topping")
        if has_topping == 'true' then
            local menu_item = get_element_dim(item)
            splash:mouse_click(menu_item.x, menu_item.y)
            splash:wait(2)
            response_list[i] = splash:html()
            splash:send_keys('<Escape>')
            splash:wait(1)
        end
    end

    return response_list
end