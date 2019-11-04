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
    local menu_item_has_toppings = splash:jsfunc([[
        function(el) {
            var json = JSON.parse(el.dataset.object);
            if (
                json.product_variations[0]
                && json.product_variations[0].topping_ids.length
            ) return true;
            return false;
        }
    ]])
    local menu_item_name = splash:jsfunc([[
    	function(el) {
    		var title = el.querySelector('.dish-name.fn.p-name');
    		return title.textContent
  		}
    ]])
  
    local enter_adress = get_element_dim_by_xpath('/html/body/div[13]/div[1]/main/div[2]/section/div[1]/div[1]/div[2]/form/div[1]/div/input')
    splash:set_viewport_full()
    splash:mouse_click(enter_adress.x, enter_adress.y)
    splash:send_text('Strada Morii 25, Brașov 500063, România')
    splash:wait(math.random(1.4,1.9))

    local verify_adress = get_element_dim_by_xpath('//*[@id="delivery-information-postal-index-form"]/div[2]/button[1]')
    splash:set_viewport_full()
    splash:mouse_click(verify_adress.x, verify_adress.y)
    splash:wait(math.random(2,2.4))
        
    local response_list = {}

    local selector = '.dish-card.h-product.menu__item'
    local menu_items = splash:select_all(selector)

    for i, item in pairs(menu_items) do
        if i > 19 then break end
        
        local has_topping = menu_item_has_toppings(item)
        if has_topping then
            local menu_item = get_element_dim(item)
            splash:mouse_click(menu_item.x, menu_item.y)
            splash:wait(math.random(1.4,1.7))
            response_list[i] = splash:png()
            splash:send_keys('<Escape>')
            splash:wait(math.random(1.4,1.7))
        end
    end

    return response_list
end