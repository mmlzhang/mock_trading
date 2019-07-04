
$(document).ready(function(){
    UpdateUserInfo();
    UpdateCurrentOrders();
    UpdateQuotation();
    UpdateUserStocks();
    UpdateAllOrders();

    window.setInterval(function () {
        UpdateQuotation();
        var pending_orders = $("#orders-pending");
        if (pending_orders.length > 0) {
            UpdateUserInfo();
            UpdateCurrentOrders();
            UpdateAllOrders();
            UpdateUserStocks();
        }
    }, 2000)
});


// 获取用户信息
function UpdateUserInfo() {
    $.ajax({
        url: '/api/user/info',
        type: 'GET',
        dataType: 'json',
        success: function (resp) {
            $('#username').html(resp.username);
            $('#fund').html(resp.fund);
            $('#orders').html(resp.orders);
            $('#pendingOrders').html(resp.pendingOrders);
        },
        error: function (resp) {
            if (resp.status == 401) {
                location.href='/login';
            } else {
                console.log(JSON.stringify(resp));
            }
        },
    });
}

// 查询行情
function SearchQuotation() {
    var instrument = $("#instrument").val();
    $.ajax({
        url: '/api/quotation?instrumentId=' + instrument,
        type: 'GET',
        dataType: 'json',
        success: function (quotations) {
            if (quotations.length > 0) {
                var quotations_html = template('quotation-list', {quotations: quotations});
                $('#quotation').html(quotations_html);
                $("#instrumentId").html(instrument)
            } else {
                console.log("股票代码错误!")
            }
            },
        error: function (resp) {
            alert(resp.responseJSON.msg);
        },
    });
}


// 更新行情
function UpdateQuotation() {
//    获取正在显示的股票id, 以轮询的方式进行刷新信息，可参考webSocket
    var instrument = $("#instrumentId").text();
    if (instrument == "") {
        instrument = "000001"
    }
    QuotationShow(instrument)
}

// 展示行情
function QuotationShow(instrument) {
//    获取正在显示的股票id, 以轮询的方式进行刷新信息，可参考webSocket
    $.ajax({
        url: '/api/quotation?instrumentId=' + instrument,
        type: 'GET',
        dataType: 'json',
        success: function (quotations) {
            if (quotations.length > 0) {
                var quotations_html = template('quotation-list', {quotations: quotations});
                $('#quotation').html(quotations_html);
                $("#instrumentId").html(instrument)
            } else {
                console.log("股票代码错误!")
            }
            },
        error: function (resp) {
            console.log(resp.responseJSON.msg);
        },
    });
}

// 修改行情当前价格
function EditNowPrice() {
    var instrumentId = $("#edit-instrument").val();
    var price = $("#edit-price").val();
    if (instrumentId == "") {
        instrumentId = $("#instrumentId").text()
    }
    var data = {"id": instrumentId, "price": price};
        $.ajax({
		url: '/api/edit/quotation',
		type: 'PUT',
        contentType: "application/json",
		dataType: 'JSON',
		data: JSON.stringify(data),
		success: function (resp) {
		    console.log(JSON.stringify(resp));
            $("#edit-instrument").val("");
            $("#edit-price").val("");
		},
		error: function (resp) {
		    alert(resp.responseJSON.msg);
		},
	});

}

// 提交股票交易订单
function BuyStockOrder() {
    var instrumentId = $("#orderInstrumentId").val();
    var instrumentCount = $("#orderInstrumentCount").val();
    var instrumentprice = $("#orderInstrumentPrice").val();
    var data = {"id": instrumentId, "count": instrumentCount, "price": instrumentprice};

    	$.ajax({
		url: '/api/order/buy',
		type: 'POST',
        contentType: "application/json",
		dataType: 'JSON',
		data: JSON.stringify(data),
		success: function (resp) {
            $("#orderInstrumentId").val("");
            $("#orderInstrumentCount").val("");
            $("#orderInstrumentPrice").val("");
            UpdateCurrentOrders();
            UpdateUserStocks();
            UpdateAllOrders();
            UpdateUserInfo();
		},
		error: function (resp) {
			alert(resp.responseJSON.msg);
		},
	});
}

// 提交股票交易订单
function SellStockOrder() {
    var instrumentId = $("#orderInstrumentId").val();
    var instrumentCount = $("#orderInstrumentCount").val();
    var instrumentprice = $("#orderInstrumentPrice").val();
    var data = {"id": instrumentId, "count": instrumentCount, "price": instrumentprice};

    	$.ajax({
		url: '/api/order/sell',
		type: 'POST',
        contentType: "application/json",
		dataType: 'JSON',
		data: JSON.stringify(data),
		success: function (resp) {
            $("#orderInstrumentId").val("");
            $("#orderInstrumentCount").val("");
            $("#orderInstrumentPrice").val("");
            UpdateCurrentOrders();
            UpdateUserStocks();
            UpdateAllOrders();
            UpdateUserInfo();

		},
		error: function (resp) {
			alert(resp.responseJSON.msg);
		},
	});
}

// 更新交易委托列表
function UpdateCurrentOrders() {
    $.get('/api/orders/current', function (orders) {
        //  script  id 值 !!
        var order_html = template('orders-list-pending', {orders: orders});
        $('#tbody').html(order_html);
    });

}

function UpdateAllOrders() {
    $.get('/api/orders', function (orders1) {
            //  script  id 值 !!
        var order_html_all = template('orders-list-all', {orderlist: orders1});
        $('#tbody-all').html(order_html_all);
    });
}

// 更新用户持仓
function UpdateUserStocks() {
    $.get('/api/stock/user', function (userStocks) {
        if (userStocks.length > 0) {
            //  script  id 值 !!
            var s_html = template('user-stocks', {userStocks: userStocks});
            $('#tbody-UserStocks').html(s_html);
        }
    });
}


// 取消订单
function CancelOrder() {
    var orderId = event.currentTarget.id;
    var data = {"id": orderId};
    $.ajax({
		url: '/api/order/cancel',
		type: 'PUT',
        contentType: "application/json",
		dataType: 'JSON',
		data: JSON.stringify(data),
		success: function (resp) {
		    UpdateCurrentOrders();
            UpdateUserStocks();
            UpdateAllOrders();
		},
		error: function (data) {
			console.log('请求失败!', data.msg)
		},
	});
};


// 资金充值
function Recharge() {
    var amount = $("#fundAmount").val();
    var data = {"amount": amount};

    	$.ajax({
		url: '/api/recharge',
		type: 'PUT',
        contentType: "application/json",
		dataType: 'JSON',
		data: JSON.stringify(data),
		success: function (resp) {
            $("#fundAmount").val("");
            UpdateUserInfo();
		},
		error: function (resp) {
			console.log('recharge请求失败!' + JSON.stringify(resp))
		},
	});
}
