(function(){
  'use strict';

  function ready(fn){ document.readyState==='loading'?document.addEventListener('DOMContentLoaded',fn):fn(); }

  ready(function(){
    /* ── Referências ─────────────────────────────────────── */
    var caminhaoSelect = document.querySelector('#id_caminhao');
    if(!caminhaoSelect) return;

    function moverClientePrincipalParaModulo(){
      var clienteField = document.getElementById('id_cliente');
      var clientesGroup = document.getElementById('clientes_adicionais-group');
      if(!clienteField || !clientesGroup){
        return;
      }

      var groupHeader = clientesGroup.querySelector('h2');
      if(groupHeader){
        groupHeader.textContent = 'CLIENTES 01 A 07';
      }

      if(clientesGroup.querySelector('.cliente-principal-slot')){
        return;
      }

      var sourceRow = clienteField.closest('.form-row') || clienteField.closest('.fieldBox') || clienteField.parentNode;
      var targetContainer = clientesGroup.querySelector('.inline-related') || clientesGroup.querySelector('.module') || clientesGroup;
      if(!sourceRow || !targetContainer){
        return;
      }

      var slot = document.createElement('div');
      slot.className = 'cliente-principal-slot';
      slot.style.cssText = 'margin:12px 0 16px;padding:14px 16px;border:1px solid rgba(0,217,166,.16);border-radius:10px;background:rgba(7,13,26,.45);';

      var titulo = document.createElement('div');
      titulo.textContent = 'Cliente 01';
      titulo.style.cssText = 'font-size:.78rem;font-weight:800;color:#8ec5ff;margin-bottom:8px;text-transform:uppercase;letter-spacing:.04em;';
      slot.appendChild(titulo);

      sourceRow.style.margin = '0';
      sourceRow.style.padding = '0';
      sourceRow.style.border = '0';
      slot.appendChild(sourceRow);
      targetContainer.parentNode.insertBefore(slot, targetContainer);
    }

    moverClientePrincipalParaModulo();

    var produtos = [];      // [{id, nome}]
    var compartimentos = []; // [{id, numero, capacidade_litros}]
    var selecionados = {};   // {compId: {produto_id, cliente_id, cliente_label, cliente_nome}}
    var lastCaminhaoVal = '';

    /* ── Container principal ─────────────────────────────── */
    var container = document.createElement('div');
    container.id = 'bocas-container';
    container.style.cssText =
      'display:none;margin:20px 0;background:linear-gradient(145deg,#0d1929 40%,#0f2235);'
      +'border:1px solid rgba(0,217,166,.18);border-radius:16px;overflow:hidden;'
      +'box-shadow:0 6px 30px rgba(0,0,0,.3);';
    container.innerHTML =
      '<div style="padding:16px 22px;border-bottom:1px solid rgba(0,217,166,.1);">'
      +'<div style="display:flex;align-items:center;gap:10px;">'
      +'<span style="font-size:1.3rem;">🥗</span>'
      +'<span style="font-size:.92rem;font-weight:900;color:#00d9a6;letter-spacing:.05em;">'
      +'MONTE SUA CARGA: BOCA > PRODUTO > CLIENTE</span>'
      +'<span style="flex:1"></span>'
      +'<span id="bocas-resumo" style="font-size:.7rem;color:#9fb0c7;"></span>'
      +'</div>'
      +'<div id="fluxo-etapas" style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;">'
      +'<span id="etapa-boca" style="font-size:.68rem;font-weight:800;padding:4px 10px;border-radius:999px;'
      +'background:rgba(59,130,246,.18);color:#8ec5ff;border:1px solid rgba(59,130,246,.32);">1. Boca</span>'
      +'<span id="etapa-produto" style="font-size:.68rem;font-weight:800;padding:4px 10px;border-radius:999px;'
      +'background:rgba(148,163,184,.12);color:#94a3b8;border:1px solid rgba(148,163,184,.2);">2. Produto</span>'
      +'<span id="etapa-cliente" style="font-size:.68rem;font-weight:800;padding:4px 10px;border-radius:999px;'
      +'background:rgba(148,163,184,.12);color:#94a3b8;border:1px solid rgba(148,163,184,.2);">3. Cliente</span>'
      +'</div>'
      +'</div>'
      +'<div style="display:grid;grid-template-columns:1fr 1fr;min-height:220px;">'
      /* Lado esquerdo: bocas */
      +'<div id="bocas-lista" style="padding:16px;border-right:1px solid rgba(0,217,166,.1);">'
      +'<div style="font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;color:#8892a4;'
      +'margin-bottom:6px;">📦 Etapa 1: Escolha a Boca</div>'
      +'<div style="font-size:.68rem;color:#5a6478;margin-bottom:12px;">'
      +'Clique em uma boca para começar.</div>'
      +'<div id="bocas-grid" style="display:flex;flex-wrap:wrap;gap:10px;"></div>'
      +'</div>'
      /* Lado direito: produtos */
      +'<div id="produtos-lista" style="padding:16px;">'
      +'<div style="font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;color:#8892a4;'
      +'margin-bottom:6px;">🧪 Etapa 2 e 3: Produto e Cliente</div>'
      +'<div style="font-size:.68rem;color:#5a6478;margin-bottom:12px;">'
      +'Depois do produto, selecione o cliente da boca.</div>'
      +'<div id="produtos-grid" style="display:flex;flex-direction:column;gap:6px;"></div>'
      +'<div id="produtos-placeholder" style="font-size:.75rem;color:#5a6478;padding:20px;text-align:center;">'
      +'👈 Primeiro escolha a boca, igual montar salada.</div>'
      +'</div>'
      +'</div>';

    // Inserir antes do inline de compartimentos
    var inlineGroup = document.getElementById('carga_compartimentos-group')
      || document.querySelector('.inline-group');
    if(inlineGroup){
      inlineGroup.parentNode.insertBefore(container, inlineGroup);
    } else {
      var fieldsets = document.querySelectorAll('#content-main fieldset');
      if(fieldsets.length){
        fieldsets[fieldsets.length-1].parentNode.insertBefore(container, fieldsets[fieldsets.length-1].nextSibling);
      }
    }

    var bocaAtiva = null; // compartimento id atualmente selecionado

    /* ── Buscar Produtos (uma vez) ───────────────────────── */
    fetch('/operacao/api/produtos/')
      .then(function(r){ return r.json(); })
      .then(function(data){ produtos = data.produtos || []; })
      .catch(function(){});

    /* ── Quando Caminhão muda ────────────────────────────── */
    function onCaminhaoChange(){
      var val = caminhaoSelect.value;
      if(val === lastCaminhaoVal) return;
      lastCaminhaoVal = val;
      if(!val){
        container.style.display = 'none';
        compartimentos = [];
        selecionados = {};
        bocaAtiva = null;
        return;
      }
      fetch('/operacao/caminhao/' + val + '/compartimentos/')
        .then(function(r){ return r.json(); })
        .then(function(data){
          compartimentos = data.compartimentos || [];
          selecionados = {};
          bocaAtiva = null;
          if(compartimentos.length){
            container.style.display = 'block';
            container.style.animation = 'none';
            container.offsetHeight;
            container.style.animation = 'fadeSlide .4s ease-out';
            renderBocas();
            renderProdutos();
            updateResumo();
          } else {
            container.style.display = 'none';
          }
        })
        .catch(function(){ container.style.display = 'none'; });
    }

    caminhaoSelect.addEventListener('change', onCaminhaoChange);

    // Select2 (usado pelo autocomplete_fields do Django admin)
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

    // Fallback: polling a cada 500ms
    setInterval(function(){
      if(caminhaoSelect.value !== lastCaminhaoVal) onCaminhaoChange();
    }, 500);

    /* ── Renderizar Bocas ────────────────────────────────── */
    function renderBocas(){
      var grid = document.getElementById('bocas-grid');
      grid.innerHTML = '';
      compartimentos.forEach(function(c){
        var card = document.createElement('div');
        card.dataset.compId = c.id;
        var sel = selecionados[c.id];
        var prodNome = sel && sel.produto_id ? getProdutoNome(sel.produto_id) : null;
        var cliNome = sel && sel.cliente_nome ? sel.cliente_nome : null;
        var cliLabel = sel && sel.cliente_label ? sel.cliente_label : null;
        var completo = !!(sel && sel.produto_id && sel.cliente_id);
        var parcial = !!(sel && sel.produto_id && !sel.cliente_id);

        card.style.cssText =
          'cursor:pointer;border-radius:12px;padding:14px 16px;min-width:110px;text-align:center;'
          +'transition:all .2s;position:relative;'
          + (completo
            ? 'background:rgba(0,217,166,.12);border:2px solid #00d9a6;'
            : (parcial
              ? 'background:rgba(245,158,11,.12);border:2px solid #f59e0b;'
            : (bocaAtiva===c.id
              ? 'background:rgba(59,130,246,.12);border:2px solid #3b82f6;'
              : 'background:#070d1a;border:2px solid rgba(0,217,166,.12);')));

        card.innerHTML =
          '<div style="font-size:1.6rem;margin-bottom:4px;">🛢️</div>'
          +'<div style="font-size:.82rem;font-weight:800;color:'+(completo?'#00d9a6':(parcial?'#f59e0b':'#dde6f0'))+';">'
          +'Boca '+c.numero+'</div>'
          +'<div style="font-size:.62rem;color:#8892a4;margin-top:2px;">'
          +Number(c.capacidade_litros).toLocaleString('pt-BR')+' L</div>'
          +(prodNome
            ? '<div style="margin-top:6px;font-size:.6rem;font-weight:700;color:#00d9a6;'
              +'background:rgba(0,217,166,.08);border-radius:6px;padding:3px 8px;">'+prodNome+'</div>'
              +(cliNome
                ? '<div style="margin-top:4px;font-size:.58rem;font-weight:700;color:#f59e0b;'
                  +'background:rgba(245,158,11,.08);border-radius:6px;padding:3px 8px;">'+(cliLabel ? cliLabel+': ' : 'Cliente: ')+cliNome+'</div>'
                : '<div style="margin-top:4px;font-size:.58rem;font-weight:700;color:#f59e0b;'
                  +'background:rgba(245,158,11,.08);border-radius:6px;padding:3px 8px;">Falta escolher cliente</div>')
              +'<div class="boca-remove" style="position:absolute;top:4px;right:6px;font-size:.65rem;'
              +'color:#ef4444;cursor:pointer;opacity:.7;" title="Remover">✕</div>'
            : '');

        card.addEventListener('click', function(e){
          if(e.target.classList.contains('boca-remove')){
            delete selecionados[c.id];
            bocaAtiva = null;
            renderBocas();
            renderProdutos();
            updateResumo();
            syncInlines();
            return;
          }
          bocaAtiva = c.id;
          renderBocas();
          renderProdutos();
        });

        card.addEventListener('mouseenter', function(){
          if(!selecionados[c.id] && bocaAtiva!==c.id)
            card.style.borderColor='rgba(0,217,166,.4)';
        });
        card.addEventListener('mouseleave', function(){
          if(!selecionados[c.id] && bocaAtiva!==c.id)
            card.style.borderColor='rgba(0,217,166,.12)';
        });

        grid.appendChild(card);
      });
    }

    /* ── Renderizar Produtos ─────────────────────────────── */
    function renderProdutos(){
      var grid = document.getElementById('produtos-grid');
      var placeholder = document.getElementById('produtos-placeholder');
      grid.innerHTML = '';

      if(!bocaAtiva){
        placeholder.style.display = 'block';
        renderEtapas('boca');
        return;
      }
      placeholder.style.display = 'none';
      renderEtapas('produto');

      var boca = compartimentos.find(function(c){ return c.id === bocaAtiva; });
      var selAtual = selecionados[bocaAtiva] || null;
      var produtoAtual = selAtual && selAtual.produto_id ? selAtual.produto_id : null;
      if(boca){
        var header = document.createElement('div');
        header.style.cssText = 'font-size:.75rem;color:#3b82f6;font-weight:700;margin-bottom:8px;';
        header.textContent = '🛢️ Boca ' + boca.numero + ' — selecione o produto:';
        grid.appendChild(header);
      }

      produtos.forEach(function(p){
        var item = document.createElement('div');
        var isSelected = produtoAtual === p.id;
        item.style.cssText =
          'padding:10px 14px;border-radius:8px;cursor:pointer;font-size:.78rem;font-weight:600;'
          +'transition:all .15s;display:flex;align-items:center;gap:8px;'
          + (isSelected
            ? 'background:rgba(0,217,166,.15);border:1px solid #00d9a6;color:#00d9a6;'
            : 'background:#070d1a;border:1px solid rgba(0,217,166,.08);color:#dde6f0;');

        item.innerHTML =
          '<span style="font-size:1rem;">'+(isSelected?'✅':'🧪')+'</span>'
          +'<span>'+p.nome+'</span>';

        item.addEventListener('mouseenter', function(){
          if(!isSelected) item.style.background = 'rgba(0,217,166,.06)';
        });
        item.addEventListener('mouseleave', function(){
          if(!isSelected) item.style.background = '#070d1a';
        });
        item.addEventListener('click', function(){
          var anterior = selecionados[bocaAtiva] || {};
          selecionados[bocaAtiva] = {
            produto_id: p.id,
            cliente_id: anterior.cliente_id || null,
            cliente_label: anterior.cliente_label || '',
            cliente_nome: anterior.cliente_nome || '',
          };
          renderBocas();
          renderProdutos();
          updateResumo();
          syncInlines();
        });

        grid.appendChild(item);
      });

      if(!produtoAtual){
        return;
      }

      renderEtapas('cliente');

      var clientes = getClientesDisponiveis();
      var cliHeader = document.createElement('div');
      cliHeader.style.cssText = 'font-size:.72rem;color:#f59e0b;font-weight:700;margin:12px 0 8px;';
      cliHeader.textContent = '👤 Agora escolha o cliente desta boca:';
      grid.appendChild(cliHeader);

      if(!clientes.length){
        var semCli = document.createElement('div');
        semCli.style.cssText = 'padding:10px 12px;border-radius:8px;background:rgba(245,158,11,.08);'
          +'border:1px solid rgba(245,158,11,.25);color:#f59e0b;font-size:.72rem;font-weight:700;';
        semCli.textContent = 'Selecione Cliente 1 ou Clientes 2 a 7 no formulário para continuar.';
        grid.appendChild(semCli);
        return;
      }

      clientes.forEach(function(c){
        var item = document.createElement('div');
        var isSelected = selAtual && selAtual.cliente_id === c.id && selAtual.cliente_label === c.label;
        item.style.cssText =
          'padding:10px 14px;border-radius:8px;cursor:pointer;font-size:.78rem;font-weight:600;'
          +'transition:all .15s;display:flex;align-items:center;gap:8px;'
          + (isSelected
            ? 'background:rgba(245,158,11,.15);border:1px solid #f59e0b;color:#f59e0b;'
            : 'background:#070d1a;border:1px solid rgba(245,158,11,.2);color:#dde6f0;');

        item.innerHTML = '<span style="font-size:1rem;">'+(isSelected ? '✅' : '👤')+'</span>'
          +'<span>'+c.label+': '+c.nome+'</span>';

        item.addEventListener('mouseenter', function(){
          if(!isSelected) item.style.background = 'rgba(245,158,11,.06)';
        });
        item.addEventListener('mouseleave', function(){
          if(!isSelected) item.style.background = '#070d1a';
        });
        item.addEventListener('click', function(){
          selecionados[bocaAtiva] = {
            produto_id: produtoAtual,
            cliente_id: c.id,
            cliente_label: c.label,
            cliente_nome: c.nome,
          };
          bocaAtiva = null;
          renderBocas();
          renderProdutos();
          updateResumo();
          syncInlines();
        });

        grid.appendChild(item);
      });
    }

    /* ── Resumo ──────────────────────────────────────────── */
    function updateResumo(){
      var el = document.getElementById('bocas-resumo');
      var total = compartimentos.length;
      var selProduto = 0;
      var selCompleto = 0;
      Object.keys(selecionados).forEach(function(k){
        var item = selecionados[k];
        if(item && item.produto_id){
          selProduto += 1;
          if(item.cliente_id){
            selCompleto += 1;
          }
        }
      });
      el.textContent = selCompleto + ' de ' + total + ' bocas completas ('+selProduto+' com produto)';
    }

    /* ── Helpers ─────────────────────────────────────────── */
    function getProdutoNome(id){
      var p = produtos.find(function(x){ return x.id === id; });
      return p ? p.nome : '';
    }

    function renderEtapas(etapa){
      var boca = document.getElementById('etapa-boca');
      var produto = document.getElementById('etapa-produto');
      var cliente = document.getElementById('etapa-cliente');
      if(!boca || !produto || !cliente) return;

      var onBlue = 'background:rgba(59,130,246,.18);color:#8ec5ff;border:1px solid rgba(59,130,246,.32);';
      var onGreen = 'background:rgba(0,217,166,.16);color:#00d9a6;border:1px solid rgba(0,217,166,.28);';
      var onAmber = 'background:rgba(245,158,11,.16);color:#f59e0b;border:1px solid rgba(245,158,11,.3);';
      var off = 'background:rgba(148,163,184,.12);color:#94a3b8;border:1px solid rgba(148,163,184,.2);';

      boca.style.cssText = boca.style.cssText.replace(/background:[^;]*;color:[^;]*;border:[^;]*;/, '');
      produto.style.cssText = produto.style.cssText.replace(/background:[^;]*;color:[^;]*;border:[^;]*;/, '');
      cliente.style.cssText = cliente.style.cssText.replace(/background:[^;]*;color:[^;]*;border:[^;]*;/, '');

      boca.style.cssText += onBlue;
      produto.style.cssText += off;
      cliente.style.cssText += off;

      if(etapa === 'produto'){
        produto.style.cssText = produto.style.cssText.replace(off, onGreen);
      }
      if(etapa === 'cliente'){
        produto.style.cssText = produto.style.cssText.replace(off, onGreen);
        cliente.style.cssText = cliente.style.cssText.replace(off, onAmber);
      }
    }

    function getClientesDisponiveis(){
      var out = [];

      var cli1 = document.getElementById('id_cliente');
      if(cli1 && cli1.value){
        var txt1 = (cli1.options && cli1.selectedIndex >= 0)
          ? (cli1.options[cli1.selectedIndex].text || '').trim()
          : '';
        out.push({
          id: parseInt(cli1.value, 10),
          nome: txt1 || 'Cliente selecionado',
          label: 'Cliente 1'
        });
      }

      var adicionais = document.querySelectorAll('select[name^="clientes_adicionais-"][name$="-cliente"]');
      adicionais.forEach(function(sel){
        if(!sel.value || sel.name.indexOf('__prefix__') !== -1){
          return;
        }
        var ordemField = sel.form ? sel.form.querySelector('input[name="'+sel.name.replace('-cliente', '-ordem')+'"]') : null;
        var ordemVal = ordemField && ordemField.value ? parseInt(ordemField.value, 10) : null;
        var ordemMatch = sel.name.match(/clientes_adicionais-(\d+)-cliente/);
        var idx = ordemMatch ? parseInt(ordemMatch[1], 10) : 0;
        var txt = (sel.options && sel.selectedIndex >= 0)
          ? (sel.options[sel.selectedIndex].text || '').trim()
          : '';
        out.push({
          id: parseInt(sel.value, 10),
          nome: txt || 'Cliente selecionado',
          label: 'Cliente ' + (ordemVal || (idx + 2))
        });
      });

      return out;
    }

    /* ── Sincronizar com Inline Django ───────────────────── */
    function syncInlines(){
      var prefix = 'carga_compartimentos';
      var totalForms = document.getElementById('id_'+prefix+'-TOTAL_FORMS');
      if(!totalForms) return;

      // Remover inputs gerados anteriormente pelo JS
      document.querySelectorAll('.synced-inline').forEach(function(el){ el.remove(); });

      // Marcar inlines originais do Django para deleção
      var existingRows = document.querySelectorAll('tr.dynamic-cargacompartimento, .dynamic-'+prefix);
      existingRows.forEach(function(row){
        var delInput = row.querySelector('input[id$="-DELETE"]');
        if(delInput){ delInput.checked = true; delInput.value = 'on'; }
        row.style.display = 'none';
      });

      var keys = Object.keys(selecionados);
      var initialForms = document.getElementById('id_'+prefix+'-INITIAL_FORMS');
      var initial = initialForms ? parseInt(initialForms.value) || 0 : 0;
      var startIdx = initial;

      keys.forEach(function(compId, i){
        var idx = startIdx + i;
        var item = selecionados[compId] || {};
        var produtoId = item.produto_id || item;
        var formHtml =
          '<input type="hidden" name="'+prefix+'-'+idx+'-compartimento" value="'+compId+'">'
          +'<input type="hidden" name="'+prefix+'-'+idx+'-produto" value="'+produtoId+'">'
          +'<input type="hidden" name="'+prefix+'-'+idx+'-cliente" value="'+(item.cliente_id||'')+'">'
          +'<input type="hidden" name="'+prefix+'-'+idx+'-id" value="">'
          +'<input type="hidden" name="'+prefix+'-'+idx+'-carga" value="">';
        var div = document.createElement('div');
        div.style.display = 'none';
        div.innerHTML = formHtml;
        div.className = 'synced-inline';
        totalForms.parentNode.appendChild(div);
      });

      totalForms.value = startIdx + keys.length;
    }

    /* ── Esconder apenas o inline padrão de compartimentos ─ */
    var inlineGrp = document.getElementById('carga_compartimentos-group');
    if(inlineGrp){
      inlineGrp.style.display = 'none';
    }

    // Quando cliente principal ou adicionais mudarem, atualizar etapa 3 visualmente
    document.addEventListener('change', function(e){
      var t = e.target;
      if(!t) return;
      if(t.id === 'id_cliente' || (t.name && t.name.indexOf('clientes_adicionais-') === 0 && t.name.indexOf('-cliente') > -1)){
        if(bocaAtiva){
          renderProdutos();
        } else {
          renderBocas();
          updateResumo();
        }
      }
    });

    /* Se já tem valor de caminhão (edição), carregar */
    /* Detectar ID da carga (URL /admin/fretes/carga/24/change/) */
    var cargaIdMatch = window.location.pathname.match(/\/carga\/(\d+)\/change\//);
    var cargaId = cargaIdMatch ? parseInt(cargaIdMatch[1], 10) : null;

    if(caminhaoSelect.value){
      lastCaminhaoVal = '';
      if(cargaId){
        /* Modo edição: carregar compartimentos do caminhão e depois as seleções salvas */
        var val = caminhaoSelect.value;
        lastCaminhaoVal = val;
        fetch('/operacao/caminhao/' + val + '/compartimentos/')
          .then(function(r){ return r.json(); })
          .then(function(data){
            compartimentos = data.compartimentos || [];
            if(!compartimentos.length){ return; }
            /* Carregar seleções salvas */
            return fetch('/operacao/carga/' + cargaId + '/selecoes/')
              .then(function(r){ return r.json(); })
              .then(function(selData){
                selecionados = {};
                (selData.selecoes || []).forEach(function(s){
                  selecionados[s.compartimento_id] = {
                    produto_id: s.produto_id,
                    cliente_id: s.cliente_id,
                    cliente_nome: s.cliente_nome || '',
                    cliente_label: '',
                  };
                });
                bocaAtiva = null;
                container.style.display = 'block';
                renderBocas();
                renderProdutos();
                updateResumo();
              });
          })
          .catch(function(){});
      } else {
        setTimeout(onCaminhaoChange, 500);
      }
    }

    /* Animação fade */
    var style = document.createElement('style');
    style.textContent = '@keyframes fadeSlide{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}';
    document.head.appendChild(style);

    /* ── Cálculo automático: litros × valor_frete_litro = valor_total_frete ── */
    var litrosField = document.getElementById('id_litros');
    var freteField = document.getElementById('id_valor_frete_litro');
    var totalField = document.getElementById('id_valor_total_frete');

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
