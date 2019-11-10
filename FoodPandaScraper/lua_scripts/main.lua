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
    local menu_item_has_modal_content = splash:jsfunc([[
        function(el) {
            var json = JSON.parse(el.dataset.object);
            if (
                json.product_variations[0].topping_ids.length
                || json.product_variations.length > 1
            ) return true;
            return false;
        }
    ]])
    local dish_modal_content = splash:jsfunc([[
        function(el) {
            var json = JSON.parse(el.dataset.object);
            var variations = json.product_variations;

            var results = {
                modal: true,
                only_toppings: false,
                only_variations: false,
                click_all_variations: false,
            };

            if (variations.length > 1) {
                var only_variations = true;
                for (var i = 0; i < variations.length; i++) {
                    if (variations[i].topping_ids.length) {
                        only_variations = false;
                        break
                    }
                }

                if (only_variations) {
                    results.only_variations = true;
                } else {
                    var topping_ids_1 = variations[0].topping_ids;
                    var topping_ids_2 = variations[1].topping_ids;

                    if (topping_ids_1.length === topping_ids_2.length) {
                        for (var i = 0; i < topping_ids_1.length; i++) {
                            if (topping_ids_1[i] !== topping_ids_2[i]) {
                                results.click_all_variations = true;
                                break;
                            }
                        }
                    } else {
                        results.click_all_variations = true;
                    }
                }
            } else {
                var topping_ids = variations[0].topping_ids;
                if (topping_ids.length) {
                    results.only_toppings = true;
                } else {
                    results.modal = false;
                }
            }

            return results;
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

    -- Click items with toppings menu and store modal content
    local modals = {}
    response['modals'] = modals
    local menu_list = splash:select('section.menu__items-wrapper > div.menu__items')
    -- local category_headers = menu_list:querySelectorAll('div.dish-category-header')
    -- local category_names = {}
    -- for i, header in ipairs(category_headers) do
    --     table.insert(category_names, header.node.textContent)
    -- end

    local category_item_lists = menu_list:querySelectorAll('ul.dish-list')
    for i, list in ipairs(category_item_lists) do
        local item_list = list:querySelectorAll('div.dish-card.h-product.menu__item')
        -- treat.as_array(modals[i])
        for j, item in ipairs(item_list) do
            local results = dish_modal_content(item)
            if results.modal then
                modals[i] = modals[i] or {}
                if results.only_toppings then
                    modals[i][j] = 'only toppings'
                elseif results.only_variations then
                    modals[i][j] = 'only variations'
                else
                    if results.click_all_variations then
                        modals[i][j] = 'click all variations'
                    else
                        modals[i][j] = 'click only first'
                    end
                end
            end

            -- local has_topping = menu_item_has_modal_content(item)
            -- if has_topping then
            --     modals[i] = modals[i] or {}
            --     local item_name = item:querySelector('h3.dish-name.fn.p-name > span').node.textContent
            --     item:click{}
            --     splash:wait(math.random(1.4, 1.7))
            --     local modal_html = splash:select('#choices-toppings-modal .modal-body').node.outerHTML
            --     splash:send_keys('<Escape>')
            --     splash:wait(math.random(1.4, 1.7))
            --     modals[i][j] = { item_name = item_name, modal_content = modal_html }
            -- end
        end
    end

    return response
end