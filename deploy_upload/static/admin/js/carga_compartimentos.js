(function(){
  'use strict';

  function ready(fn){ document.readyState==='loading'?document.addEventListener('DOMContentLoaded',fn):fn(); }

  ready(function(){
    /* ── Referências ─────────────────────────────────────── */
    var caminhaoSelect = document.querySelector('#id_caminhao');
    if(!caminhaoSelect) return;

    var clienteMainSelect = document.querySelector('#id_cliente');
    var litrosField = document.getElementById('id_litros');
    var freteField = document.getElementById('id_valor_frete_litro');
    var totalField = document.getElementById('id_valor_total_frete');

    var produtos = [];
    var clientes = [];
    var compartimentos = [];
    var clienteSlots = [];
    var slotCounter = 0;
    var lastCaminhaoVal = '';

    var COLORS = ['#00d9a6','#3b82f6','#a855f7','#f97316','#ec4899','#14b8a6','#eab308'];
    var COLORS_BG = ['rgba(0,217,166,.10)','rgba(59,130,246,.10)','rgba(168,85,247,.10)','rgba(249,115,22,.10)','rgba(236,72,153,.10)','rgba(20,184,166,.10)','rgba(234,179,8,.10)'];

    /* ── Container principal ─────────────────────────────── */
    var container = document.createElement('div');
    container.id = 'bocas-container';
    container.style.cssText =
      'display:none;margin:20px 0;background:linear-gradient(145deg,#0d1929 40%,#0f2235);'
      +'border:1px solid rgba(0,217,166,.18);border-radius:16px;overflow:hidden;'
      +'box-shadow:0 6px 30px rgba(0,0,0,.3);';
    container.innerHTML =
      '<div style="padding:16px 22px;display:flex;align-items:center;gap:10px;'
      +'border-bottom:1px solid rgba(0,217,166,.1);">'
      +'<span style="font-size:1.3rem;">🛢️</span>'
      +'<span style="font-size:.9rem;font-weight:800;color:#00d9a6;letter-spacing:.04em;">'
      +'DISTRIBUIÇÃO DE BOCAS POR CLIENTE</span>'
      +'<span style="flex:1"></span>'
      +'<span id="bocas-resumo" style="font-size:.7rem;color:#8892a4;"></span>'
      +'</div>'
      +'<div id="slots-area" style="padding:16px;display:flex;flex-direction:column;gap:14px;"></div>'
      +'<div style="padding:0 16px 16px;display:flex;align-items:center;gap:12px;">'
      +'<button type="button" id="btn-add-cliente" style="background:rgba(0,217,166,.08);'
      +'border:1px dashed rgba(0,217,166,.35);border-radius:10px;color:#00d9a6;padding:10px 20px;'
      +'cursor:pointer;font-size:.78rem;font-weight:700;transition:all .2s;display:flex;align-items:center;gap:6px;">'
      +'<span style="font-size:1.1rem;">＋</span> Adicionar Cliente</button>'
      +'<span id="bocas-summary" style="font-size:.7rem;color:#8892a4;margin-left:auto;"></span>'
      +'</div>';

    var inlineGroup = document.querySelector('.inline-group');
    if(inlineGroup){
      inlineGroup.parentNode.insertBefore(container, inlineGroup);
    } else {
      var fieldsets = document.querySelectorAll('#content-main fieldset');
      if(fieldsets.length){
        fieldsets[fieldsets.length-1].parentNode.insertBefore(container, fieldsets[fieldsets.length-1].nextSibling);
      }
    }

    document.getElementById('btn-add-cliente').addEventListener('click', function(){
      addSlot();
    });
    document.getElementById('btn-add-cliente').addEventListener('mouseenter', function(){
      this.style.background='rgba(0,217,166,.18)';
    });
    document.getElementById('btn-add-cliente').addEventListener('mouseleave', function(){
      this.style.background='rgba(0,217,166,.08)';
    });

    /* ── Buscar Produtos e Clientes ──────────────────────── */
    fetch('/operacao/api/produtos/')
      .then(function(r){ return r.json(); })
      .then(function(data){ produtos = data.produtos || []; })
      .catch(function(){});

    fetch('/operacao/api/clientes/')
      .then(function(r){ return r.json(); })
      .then(function(data){ clientes = data.clientes || []; })
      .catch(function(){});

    /* ── Quando Caminhão muda ────────────────────────────── */
    function onCaminhaoChange(){
      var val = caminhaoSelect.value;
      if(val === lastCaminhaoVal) return;
      lastCaminhaoVal = val;
      if(!val){
        container.style.display = 'none';
        compartimentos = [];
        clienteSlots = [];
        slotCounter = 0;
        return;
      }
      fetch('/operacao/caminhao/' + val + '/compartimentos/')
        .then(function(r){ return r.json(); })
        .then(function(data){
          compartimentos = data.compartimentos || [];
          if(compartimentos.length){
            container.style.display = 'block';
            container.style.animation = 'none';
            container.offsetHeight;
            container.style.animation = 'fadeSlide .4s ease-out';
            if(clienteSlots.length === 0){
              addSlot();
            }
            renderAll();
          } else {
            container.style.display = 'none';
          }
        })
        .catch(function(){ container.style.display = 'none'; });
    }

    caminhaoSelect.addEventListener('change', onCaminhaoChange);

    function bindSelect2(){
      if(window.django && window.django.jQuery){
        django.jQuery('#id_caminhao').on('select2:select select2:clear change', onCaminhaoChange);
        return true;
      }
      return false;
    }
    if(!bindSelect2()){
      var s2tries = 0;
      var s2interval = setInterval(function(){
        if(bindSelect2() || ++s2tries > 30) clearInterval(s2interval);
      }, 200);
    }
    setInterval(function(){
      if(caminhaoSelect.value !== lastCaminhaoVal) onCaminhaoChange();
    }, 500);

    /* ── Helpers ─────────────────────────────────────────── */
    function getAssignedBocas(excludeSlotId){
      var assigned = {};
      clienteSlots.forEach(function(s){
        if(s.id !== excludeSlotId){
          s.bocas.forEach(function(compId){ assigned[compId] = true; });
        }
      });
      return assigned;
    }

    function getColor(idx){ return COLORS[idx % COLORS.length]; }
    function getColorBg(idx){ return COLORS_BG[idx % COLORS_BG.length]; }

    function getSlotIndex(slotId){
      for(var i=0;i<clienteSlots.length;i++){
        if(clienteSlots[i].id === slotId) return i;
      }
      return 0;
    }

    /* ── Adicionar Slot de Cliente ────────────────────────── */
    function addSlot(presetCliente, presetProduto, presetBocas){
      slotCounter++;
      var slot = {
        id: slotCounter,
        clienteId: presetCliente || null,
        produtoId: presetProduto || null,
        bocas: presetBocas || []
      };
      clienteSlots.push(slot);
      renderAll();
      return slot;
    }

    function removeSlot(slotId){
      clienteSlots = clienteSlots.filter(function(s){ return s.id !== slotId; });
      renderAll();
      syncInlines();
      updateAutoFields();
    }

    /* ── Renderizar Todo ─────────────────────────────────── */
    function renderAll(){
      var area = document.getElementById('slots-area');
      area.innerHTML = '';
      clienteSlots.forEach(function(slot, idx){
        area.appendChild(renderSlot(slot, idx));
      });
      updateSummary();
    }

    /* ── Renderizar um Slot ──────────────────────────────── */
    function renderSlot(slot, idx){
      var color = getColor(idx);
      var colorBg = getColorBg(idx);
      var assigned = getAssignedBocas(slot.id);

      var card = document.createElement('div');
      card.style.cssText =
        'background:'+colorBg+';border:1px solid '+color+'33;border-left:4px solid '+color+';'
        +'border-radius:12px;padding:16px;position:relative;transition:all .2s;';

      /* Header */
      var header = document.createElement('div');
      header.style.cssText = 'display:flex;align-items:center;gap:10px;margin-bottom:14px;flex-wrap:wrap;';

      var label = document.createElement('span');
      label.style.cssText = 'font-size:.75rem;font-weight:800;color:'+color+';text-transform:uppercase;letter-spacing:.06em;';
      label.textContent = '👤 Cliente ' + (idx + 1);
      header.appendChild(label);

      /* Cliente select */
      var cSelect = document.createElement('select');
      cSelect.style.cssText =
        'flex:1;min-width:180px;background:#0a1525;color:#dde6f0;border:1px solid '+color+'44;'
        +'border-radius:8px;padding:8px 12px;font-size:.78rem;font-weight:600;cursor:pointer;'
        +'appearance:auto;';
      cSelect.innerHTML = '<option value="">— Selecione o cliente —</option>';
      clientes.forEach(function(c){
        var opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = c.nome;
        if(slot.clienteId == c.id) opt.selected = true;
        cSelect.appendChild(opt);
      });
      cSelect.addEventListener('change', function(){
        slot.clienteId = this.value ? parseInt(this.value) : null;
        syncInlines();
        updateAutoFields();
      });
      header.appendChild(cSelect);

      /* Produto select */
      var pLabel = document.createElement('span');
      pLabel.style.cssText = 'font-size:.65rem;color:#8892a4;font-weight:600;margin-left:4px;';
      pLabel.textContent = '🧪 Produto:';
      header.appendChild(pLabel);

      var pSelect = document.createElement('select');
      pSelect.style.cssText =
        'min-width:140px;background:#0a1525;color:#dde6f0;border:1px solid '+color+'44;'
        +'border-radius:8px;padding:8px 12px;font-size:.78rem;font-weight:600;cursor:pointer;'
        +'appearance:auto;';
      pSelect.innerHTML = '<option value="">— Produto —</option>';
      produtos.forEach(function(p){
        var opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.nome;
        if(slot.produtoId == p.id) opt.selected = true;
        pSelect.appendChild(opt);
      });
      pSelect.addEventListener('change', function(){
        slot.produtoId = this.value ? parseInt(this.value) : null;
        syncInlines();
        updateAutoFields();
      });
      header.appendChild(pSelect);

      /* Remove button */
      if(clienteSlots.length > 1){
        var removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.style.cssText =
          'background:rgba(239,68,68,.1);color:#ef4444;border:1px solid rgba(239,68,68,.25);'
          +'border-radius:8px;padding:6px 12px;font-size:.7rem;font-weight:700;cursor:pointer;'
          +'transition:all .18s;margin-left:auto;';
        removeBtn.textContent = '✕ Remover';
        removeBtn.addEventListener('click', function(){ removeSlot(slot.id); });
        removeBtn.addEventListener('mouseenter', function(){ this.style.background='rgba(239,68,68,.25)'; });
        removeBtn.addEventListener('mouseleave', function(){ this.style.background='rgba(239,68,68,.1)'; });
        header.appendChild(removeBtn);
      }

      card.appendChild(header);

      /* Bocas grid */
      var bocasDiv = document.createElement('div');
      bocasDiv.style.cssText = 'display:flex;flex-wrap:wrap;gap:8px;';

      compartimentos.forEach(function(c){
        var isInSlot = slot.bocas.indexOf(c.id) !== -1;
        var isAssigned = assigned[c.id];

        var boca = document.createElement('div');
        boca.style.cssText =
          'border-radius:10px;padding:10px 14px;min-width:100px;text-align:center;'
          +'transition:all .2s;cursor:'+(isAssigned?'not-allowed':'pointer')+';'
          +'opacity:'+(isAssigned?'0.3':'1')+';'
          + (isInSlot
            ? 'background:'+color+'22;border:2px solid '+color+';'
            : 'background:#070d1a;border:2px solid rgba(255,255,255,.06);');

        var litrosTxt = Number(c.capacidade_litros).toLocaleString('pt-BR');
        boca.innerHTML =
          '<div style="font-size:1.3rem;margin-bottom:2px;">'+(isInSlot?'✅':'🛢️')+'</div>'
          +'<div style="font-size:.78rem;font-weight:800;color:'+(isInSlot?color:'#dde6f0')+';">Boca '+c.numero+'</div>'
          +'<div style="font-size:.6rem;color:#8892a4;margin-top:1px;">'+litrosTxt+' L</div>';

        if(!isAssigned){
          boca.addEventListener('click', function(){
            var idx2 = slot.bocas.indexOf(c.id);
            if(idx2 !== -1){
              slot.bocas.splice(idx2, 1);
            } else {
              slot.bocas.push(c.id);
            }
            renderAll();
            syncInlines();
            updateAutoFields();
          });
          boca.addEventListener('mouseenter', function(){
            if(slot.bocas.indexOf(c.id)===-1)
              boca.style.borderColor = color+'66';
          });
          boca.addEventListener('mouseleave', function(){
            if(slot.bocas.indexOf(c.id)===-1)
              boca.style.borderColor = 'rgba(255,255,255,.06)';
          });
        }

        bocasDiv.appendChild(boca);
      });

      card.appendChild(bocasDiv);

      /* Subtotal */
      var subtotal = 0;
      slot.bocas.forEach(function(compId){
        var comp = compartimentos.find(function(c){ return c.id === compId; });
        if(comp) subtotal += comp.capacidade_litros;
      });
      if(slot.bocas.length > 0){
        var subDiv = document.createElement('div');
        subDiv.style.cssText =
          'margin-top:10px;font-size:.7rem;color:'+color+';font-weight:700;'
          +'display:flex;align-items:center;gap:6px;';
        subDiv.textContent = '📊 ' + slot.bocas.length + ' boca(s) • '
          + Number(subtotal).toLocaleString('pt-BR') + ' L';
        card.appendChild(subDiv);
      }

      return card;
    }

    /* ── Resumo ──────────────────────────────────────────── */
    function updateSummary(){
      var el = document.getElementById('bocas-resumo');
      var el2 = document.getElementById('bocas-summary');
      var totalBocas = compartimentos.length;
      var usedBocas = 0;
      var totalLitros = 0;
      clienteSlots.forEach(function(s){
        usedBocas += s.bocas.length;
        s.bocas.forEach(function(compId){
          var comp = compartimentos.find(function(c){ return c.id === compId; });
          if(comp) totalLitros += comp.capacidade_litros;
        });
      });
      var txt = usedBocas + ' de ' + totalBocas + ' bocas • ' + Number(totalLitros).toLocaleString('pt-BR') + ' L';
      if(el) el.textContent = txt;
      if(el2) el2.textContent = txt;

      /* Disable add button if all bocas assigned */
      var btn = document.getElementById('btn-add-cliente');
      if(btn){
        if(usedBocas >= totalBocas){
          btn.style.opacity = '0.4';
          btn.style.pointerEvents = 'none';
        } else {
          btn.style.opacity = '1';
          btn.style.pointerEvents = 'auto';
        }
      }
    }

    /* ── Auto-fill Carga fields ──────────────────────────── */
    function updateAutoFields(){
      /* Auto-fill main Carga.cliente from first slot */
      if(clienteMainSelect && clienteSlots.length > 0 && clienteSlots[0].clienteId){
        var val = String(clienteSlots[0].clienteId);
        if(window.django && window.django.jQuery){
          var $sel = django.jQuery('#id_cliente');
          if($sel.length && $sel.val() != val){
            /* For select2, we need to set the option and trigger */
            var optExists = $sel.find('option[value="'+val+'"]').length > 0;
            if(!optExists){
              var cliObj = clientes.find(function(c){ return c.id == val; });
              var optText = cliObj ? cliObj.nome : val;
              $sel.append(new Option(optText, val, true, true));
            }
            $sel.val(val).trigger('change');
          }
        } else {
          clienteMainSelect.value = val;
        }
      }

      /* Auto-calc litros from total selected bocas */
      if(litrosField){
        var totalLitros = 0;
        clienteSlots.forEach(function(s){
          s.bocas.forEach(function(compId){
            var comp = compartimentos.find(function(c){ return c.id === compId; });
            if(comp) totalLitros += comp.capacidade_litros;
          });
        });
        if(totalLitros > 0){
          litrosField.value = totalLitros.toFixed(2).replace('.', ',');
        }
      }

      calcularTotal();
    }

    /* ── Sincronizar com Inline Django ───────────────────── */
    function syncInlines(){
      var prefix = 'carga_compartimentos';
      var totalForms = document.getElementById('id_'+prefix+'-TOTAL_FORMS');
      if(!totalForms) return;

      document.querySelectorAll('.synced-inline').forEach(function(el){ el.remove(); });

      var existingRows = document.querySelectorAll('tr.dynamic-cargacompartimento, .dynamic-'+prefix);
      existingRows.forEach(function(row){
        var delInput = row.querySelector('input[id$="-DELETE"]');
        if(delInput){ delInput.checked = true; delInput.value = 'on'; }
        row.style.display = 'none';
      });

      var initialForms = document.getElementById('id_'+prefix+'-INITIAL_FORMS');
      var initial = initialForms ? parseInt(initialForms.value) || 0 : 0;
      var startIdx = initial;
      var formIdx = startIdx;

      clienteSlots.forEach(function(slot){
        if(!slot.produtoId) return;
        slot.bocas.forEach(function(compId){
          var html =
            '<input type="hidden" name="'+prefix+'-'+formIdx+'-compartimento" value="'+compId+'">'
            +'<input type="hidden" name="'+prefix+'-'+formIdx+'-produto" value="'+slot.produtoId+'">'
            +'<input type="hidden" name="'+prefix+'-'+formIdx+'-cliente" value="'+(slot.clienteId||'')+'">'
            +'<input type="hidden" name="'+prefix+'-'+formIdx+'-id" value="">'
            +'<input type="hidden" name="'+prefix+'-'+formIdx+'-carga" value="">';
          var div = document.createElement('div');
          div.style.display = 'none';
          div.innerHTML = html;
          div.className = 'synced-inline';
          totalForms.parentNode.appendChild(div);
          formIdx++;
        });
      });

      totalForms.value = formIdx;
    }

    /* ── Esconder inline padrão ──────────────────────────── */
    var inlineGrp = document.querySelector('.inline-group');
    if(inlineGrp){
      inlineGrp.style.display = 'none';
    }

    /* ── Restaurar dados no modo edição ──────────────────── */
    function restoreFromInlines(){
      var prefix = 'carga_compartimentos';
      var totalForms = document.getElementById('id_'+prefix+'-TOTAL_FORMS');
      if(!totalForms) return;
      var total = parseInt(totalForms.value) || 0;
      if(total === 0) return;

      var groups = {}; // key = clienteId + '|' + produtoId, value = {clienteId, produtoId, bocas:[]}
      for(var i=0; i<total; i++){
        var compInput = document.querySelector('[name="'+prefix+'-'+i+'-compartimento"]');
        var prodInput = document.querySelector('[name="'+prefix+'-'+i+'-produto"]');
        var cliInput = document.querySelector('[name="'+prefix+'-'+i+'-cliente"]');
        var delInput = document.querySelector('[name="'+prefix+'-'+i+'-DELETE"]');
        if(delInput && (delInput.checked || delInput.value === 'on')) continue;
        if(!compInput || !compInput.value) continue;

        var compId = parseInt(compInput.value);
        var prodId = prodInput ? parseInt(prodInput.value) || null : null;
        var cliId = cliInput ? parseInt(cliInput.value) || null : null;

        var key = (cliId||'null') + '|' + (prodId||'null');
        if(!groups[key]){
          groups[key] = { clienteId: cliId, produtoId: prodId, bocas: [] };
        }
        groups[key].bocas.push(compId);
      }

      var keys = Object.keys(groups);
      if(keys.length > 0){
        clienteSlots = [];
        slotCounter = 0;
        keys.forEach(function(k){
          var g = groups[k];
          addSlot(g.clienteId, g.produtoId, g.bocas);
        });
      }
    }

    /* Se já tem valor de caminhão (edição), carregar */
    if(caminhaoSelect.value){
      lastCaminhaoVal = '';
      setTimeout(function(){
        onCaminhaoChange();
        /* Wait for compartimentos to load, then restore */
        setTimeout(function(){
          if(compartimentos.length > 0){
            restoreFromInlines();
            renderAll();
            syncInlines();
          }
        }, 800);
      }, 500);
    }

    /* Animação fade */
    var style = document.createElement('style');
    style.textContent =
      '@keyframes fadeSlide{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}'
      +'#bocas-container select:focus{outline:none;box-shadow:0 0 0 2px rgba(0,217,166,.3);}';
    document.head.appendChild(style);

    /* ── Cálculo automático: litros × valor_frete_litro = valor_total_frete ── */
    function calcularTotal(){
      if(!litrosField || !freteField || !totalField) return;
      var litros = parseFloat(litrosField.value.replace(',', '.')) || 0;
      var frete = parseFloat(freteField.value.replace(',', '.')) || 0;
      if(litros > 0 && frete > 0){
        var total = (litros * frete).toFixed(2).replace('.', ',');
        totalField.value = total;
      }
    }

    if(litrosField && freteField){
      litrosField.addEventListener('input', calcularTotal);
      freteField.addEventListener('input', calcularTotal);
      litrosField.addEventListener('change', calcularTotal);
      freteField.addEventListener('change', calcularTotal);
    }
  });
})();
