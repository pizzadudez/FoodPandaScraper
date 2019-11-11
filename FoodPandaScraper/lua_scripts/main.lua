function main(splash)
    treat = require("treat")
    splash.private_mode_enabled = false
    assert(splash:go(splash.args.url))
    splash:wait(2)

    ---------------------------------------------------------------------------
    -- JS Helpers
    ---------------------------------------------------------------------------
    local coordinates = splash:jsfunc([[
        function() {
            var url = document.querySelector('img.map');
            return url.dataset.imgUrl.match(/\d+.\d+,\d+.\d+/);
        }
    ]])
    local get_topping_id = splash:jsfunc([[
        function(el) {
            return el.dataset.toppingId;
        }
    ]])
    local dish_modal_content = splash:jsfunc([[
        function(el) {
            var json = JSON.parse(el.dataset.object);
            var variations = json.product_variations;

            var results = {
                modal: true,
                only_toppings: false,
                click_all_variations: false,
            };
            var topping_id_map = {}

            if (variations.length > 1) {
                results.modal = false;
                for (var i = 0; i < variations.length; i++) {
                    if (variations[i].topping_ids.length) {
                        results.modal = true;
                        break;
                    }
                }

                if (results.modal) {
                    for (var i = 1; i < variations.length; i++) {
                        if (
                            JSON.stringify(variations[i-1].topping_ids) 
                            !== JSON.stringify(variations[i].topping_ids)
                        ) {
                            results.click_all_variations = true;
                            break;
                        }
                    }

                    for (var i = 0; i < variations.length; i++) {
                        var topping_ids = variations[i].topping_ids;
                        for (var j = 0; j < topping_ids.length; j++) {
                            var topping_id = topping_ids[i];
                            topping_id_map[topping_id] = true;
                        }
                    }
                } 
            } else {
                var topping_ids = variations[0].topping_ids;
                if (topping_ids.length) {
                    results.only_toppings = true;
                    for (var i = 0; i < topping_ids.length; i++) {
                        var topping_id = topping_ids[i];
                        topping_id_map[topping_id] = true;
                    }
                } else {
                    results.modal = false;
                }
            }
            results.topping_id_map = topping_id_map;
            return results;
        }
    ]])
    local is_modal_open = splash:jsfunc([[
        function() {
            var display = document.querySelector('#choices-toppings-modal')
            if (!display) return false;
            
            return display.style.display === 'none' ? false : true;
        }
    ]])

    ---------------------------------------------------------------------------
    -- Lua Script
    ---------------------------------------------------------------------------
    local response = {}
    -- Submit Address and get page HTML
    local coords = coordinates()
    -- local address = assert(splash:select('.vendor-location')).node.textContent
    local address_input = assert(splash:select('.restaurants-search-form__input'))
    local address_verify_button = assert(splash:select('.restaurants-search-form__button--full'))
    splash:set_viewport_full()
    address_input:mouse_click{}
    splash:send_text(coords)
    address_verify_button:mouse_click{}
    splash:wait(1.9)
    response['html'] = splash:html()

    -- Click items with modal content and store topping_selectors
    local topping_selectors = {}
    response['topping_selectors'] = topping_selectors

    -- local func
    local add_topping_selectors = function()
        local modal = splash:select('#choices-toppings-modal .modal-body')
        local toppings = modal:querySelectorAll('div.topping')
        for _, topping in ipairs(toppings) do
            local topping_container = topping:querySelector('div.product-topping-list')
            local topping_id = get_topping_id(topping_container)
            topping_selectors[topping_id] = topping_selectors[topping_id] or topping.node.outerHTML
        end
    end
    -- local func
    local has_new_toppings = function(map)
        for topping_id, _ in pairs(map) do
            if not topping_selectors[topping_id] then return true end;
        end
        return false;
    end

    -- Loop over all dishes to get topping selectors
    local dishes = splash:select_all('div.dish-card.menu__item')
    for _, dish in ipairs(dishes) do
        local dish_name = dish:querySelector('h3.dish-name.fn.p-name > span').node.textContent
        local results = dish_modal_content(dish)
        
        -- Dish has modal
        if results.modal and has_new_toppings(results.topping_id_map) then
            dish:click{}
            while not is_modal_open() do
                splash:wait(math.random(0.2, 0.4))
            end
            local modal = splash:select('#choices-toppings-modal .modal-body')
            if not results.only_toppings and not results.only_variations then
                local variations = modal:querySelectorAll('div.product-topping-item')
                for _, variation in ipairs(variations) do
                    variation:click{}
                    splash:wait(math.random(0.5, 0.7))
                    add_topping_selectors()
                    if not results.click_all_variations then
                        break;
                    end
                end
            elseif results.only_toppings then
                add_topping_selectors()
            end
            -- done, close modal
            splash:send_keys('<Escape>')
            while is_modal_open() do
                splash:wait(math.random(0.2, 0.4))
            end
        end
    end

    return response
end