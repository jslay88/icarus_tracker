// ==UserScript==
// @name         Icarus Tracker
// @namespace    https://icarus-tracker.k8s.jslay.net/api/v1/
// @version      0.5
// @updateURL    https://icarus-tracker.k8s.jslay.net/static/userscript/update.js
// @downloadURL  https://icarus-tracker.k8s.jslay.net/static/userscript/script.js
// @description  Track mined caves for multiple sessions and users
// @author       jslay
// @match        https://www.icarusintel.com/
// @icon         https://www.icarusintel.com/icon/page2.png
// @require      https://cdn.jsdelivr.net/npm/axios@^0.22.0/dist/axios.min.js
// @require      https://cdnjs.cloudflare.com/ajax/libs/js-cookie/2.2.1/js.cookie.min.js
// @require      https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.min.js
// @require      https://cdn.jsdelivr.net/npm/vue@2.6.14/dist/vue.js
// @resource     bootstrapCSS https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css
// @resource     customCSS    https://icarus-tracker.k8s.jslay.net/static/userscript/style.css
// @grant        GM.xmlHttpRequest
// @grant        GM_getResourceText
// @grant        GM_addStyle
// ==/UserScript==

(function() {
  'use strict';
  console.log('Initializing Icarus Tracker...')
  const scheme = 'https'
  const baseAPIUrl = 'icarus-tracker.k8s.jslay.net'
  const idExpr = new RegExp('ID: (\\d+)')

  // Style Sheets
  GM_addStyle(GM_getResourceText('bootstrapCSS'))
  GM_addStyle(GM_getResourceText('customCSS'))

  // Build div for Vue App
  const panelContainer = document.createElement('div')
  panelContainer.id = 'icarusTracker'
  console.log('Injecting HTML Container...')
  document.getElementsByTagName('body')[0].appendChild(panelContainer)

  console.log('Hook Application...')
  let app = new Vue({
    el: '#icarusTracker',
    data: {
      addingSession: false,
      blockListener: false,
      caves: Array(),
      deletingSession: false,
      selectedSessionId: null,
      sessionInput: '',
      socket: null,
      user: {
        id: Cookies.get('it_token'),
        username: null,
        game_sessions: Array()
      }
    },
    template: `
      <div class="container bg-dark text-light bg-opacity-75 rounded px-2 py-3 panelContainer" id="icarusTracker">
        <h3 class="text-warning pb-2">Icarus Tracker</h3>
        <h5 class="text-warning float-end m-2" v-if="user.username">{{ user.username }}</h5>
        <div class="mx-auto w-75 border border-warning rounded p-2 shadow" v-if="user.username == null">
          <div class="text-center">Sign In</div>
          <label for="userTokenInput">User Token</label>
          <input type="text" class="form-control" v-model="user.id" maxlength="36">
          <button class="btn btn-warning w-100 mt-2" :disabled="!user.id || user.id.length !== 36" v-on:click="signIn">Sign In</button>
        </div>
        <div class="mx-auto w-auto border border-warning rounded p-2 shadow" v-else>
          <h4 class="text-warning">Game Sessions</h4>
          <div class="container" v-if="addingSession">
            <input class="form-control p-2" type="text" v-model="sessionInput" placeholder="Existing Session ID or New Session Description">
            <div class="text-center p-2">
              <button class="btn btn-warning mx-auto w-25" v-on:click="addSession">Add Session</button>
              <button class="btn btn-secondary mx-auto w-25" v-on:click="sessionInput = ''; addingSession = false">Cancel</button>
            </div>
          </div>
          <div class="text-center" v-else>
            <p v-if="user.game_sessions && !user.game_sessions.length">
              No Game Sessions Found
            </p>
            <div class="p-2 row" v-else>
              <select v-model="selectedSessionId" class="form-select w-50 mx-auto" v-if="!deletingSession" v-on:change="loadSession">
                <option v-for="game_session in user.game_sessions" v-bind:value="game_session.id">{{ game_session.name }}</option>
              </select>
            </div>
            <div class="text-center mb-2" v-if="deletingSession">
                <h4>Delete {{ selectedSession.name }}?</h4>
            </div>
            <button v-bind:class="['btn', 'btn-warning', 'mx-auto', selectedSessionId ? 'w-25' : 'w-50']" v-on:click="addingSession = true" v-if="!deletingSession">Add Session</button>
            <button class="btn btn-danger w-25 mx-auto" v-if="selectedSessionId && !deletingSession" v-on:click="deletingSession = true">Delete Session</button>
            <button class="btn btn-danger w-25 mx-auto" v-if="deletingSession" v-on:click="deleteSession">Are you sure?</button>
            <button class="btn btn-secondary mx-auto w-25" v-if="deletingSession" v-on:click="deletingSession = false">Cancel</button>
          </div>
        </div>
        <div class="text-center text-muted pt-3">&copy;2022 - jslay</div>
      </div>
    `,
    computed: {
      selectedSession: function() {
        for (let i = 0; i < this.user.game_sessions.length; i++) {
          if (this.user.game_sessions[i].id === this.selectedSessionId) {
            return this.user.game_sessions[i]
          }
        }
      }
    },
    methods: {
      addCallbackListener(cave) {
        cave.addEventListener('click', (e) => {
          if (!this.selectedSessionId || this.blockListener) {
            return
          }
          if (e.target.getIcon() !== mined) {
            // console.log('Marking Unmined')
            this.deleteMarker(e.target, false)
            return
          }
          // console.log('Marking Mined')
          this.addMarker(e.target, false)
        })
      },
      discoverCaves() {
        console.log('Discovering Caves...')
        for(let i=1; i < 300; i++) {
          // console.log(`Grabbing c${i}...`)
          try {
            let cave = eval(`c${i}`)
            this.addCallbackListener(cave)
            this.caves.push(cave)
          }
          catch(e) {
            // console.log(`Cave c${i} undefined`)
          }
        }
        console.log(`Discovered ${this.caves.length} caves`)
      },
      async signIn() {
        try {
          let response = await axios.get(`${scheme}://${baseAPIUrl}/api/v1/user/${this.user.id}`)
          this.user = response.data
          Cookies.set('it_token', response.data.id, { expires: 2920 })
        } catch (e) {
          console.warn(e)
        }
      },
      async addSession() {
        // console.log(`Add Session: ${this.sessionInput}`)
        try {
          let response = await axios.post(`${scheme}://${baseAPIUrl}/api/v1/user/${this.user.id}/game_session`, {name: this.sessionInput})
          this.user.game_sessions.push(response.data)
        } catch (e) {
          console.warn(e)
        }
        this.sessionInput = ''
        this.addingSession = false
      },
      async deleteSession() {
        try {
          await axios.delete(`${scheme}://${baseAPIUrl}/api/v1/user/${this.user.id}/game_session/${this.selectedSessionId}`)
          for (let i=0; i < this.user.game_sessions.length; i++) {
            if (this.user.game_sessions[i].id === this.selectedSessionId) {
              this.user.game_sessions.splice(i, 1)
              this.selectedSessionId = null
              this.deletingSession = false
              break
            }
          }
        } catch (e) {
          console.warn(e)
        }
      },
      async loadSession() {
        this.copySessionId()
        if (this.socket) {
          this.socket.close()
          this.socket = null
        }
        try {
          let response = await axios.get(`${scheme}://${baseAPIUrl}/api/v1/user/${this.user.id}/game_session/${this.selectedSessionId}`)
          for (let i=0; i < this.user.game_sessions.length; i++) {
            if (this.user.game_sessions[i].id.toString() === this.selectedSessionId) {
              Vue.set(this.user.game_sessions, i, response.data)
              break
            }
          }
        } catch (e) {
          console.warn(e)
        }
        this.caves.forEach((cave) => {
          if (cave.getIcon() === mined) {
            cave.setIcon(cave.tempIcon)
          }
        })
        // console.log(`Load Session: ${this.selectedSessionId}`)
        for (let i = 0; i < this.user.game_sessions.length; i++) {
          if (this.user.game_sessions[i].id === this.selectedSessionId) {
            this.user.game_sessions[i].markers.forEach((marker) => {
              // console.log(`Maker Loaded: ${marker.id}`)
              let cave = eval(`c${marker.id}`)
              if (cave.getIcon() !== mined) {
                cave.setIcon(mined)
              }
            })
          }
        }
        this.socket = new WebSocket(`wss://${baseAPIUrl}/ws/${this.selectedSessionId}`)
        this.socket.addEventListener('message', (message) => {
          // console.log(message)
          let data = JSON.parse(message.data)
          let cave = eval(`c${data['id']}`)
          if (!cave) {
            return
          }
          if (data['action'] === 'add') {
            // console.log(`Socket Add: c${data['id']}`)
            this.addMarker(cave, true)
          } else if (data['action'] === 'remove') {
            // console.log(`Socket Remove: c${data['id']}`)
            this.deleteMarker(cave, true)
          }
        })
      },
      copySessionId() {
        navigator.clipboard.writeText(this.selectedSessionId)
      },
      async addMarker(cave, fromSocket) {
        let caveId = cave.getPopup()._content.match(idExpr)
        if (!caveId) {
          console.warn(`Unable to parse cave ID from: ${cave.getPopup()._content}`)
          return
        }
        try {
          if (!fromSocket) {
            await axios.post(`${scheme}://${baseAPIUrl}/api/v1/user/${this.user.id}/game_session/${this.selectedSessionId}/marker/${caveId[1]}`)
          }
          for (let i = 0; i < this.user.game_sessions.length; i++) {
            if (this.user.game_sessions[i].id.toString() === this.selectedSessionId) {
              this.user.game_sessions[i].markers.push({id: caveId[1], game_session_id: this.selectedSessionId})
              break
            }
          }
          // console.log('Set Mined Icon')
          cave.setIcon(mined)
        } catch (e) {
          console.warn(e)
        }
      },
      async deleteMarker(cave, fromSocket) {
        // console.log('Deleting marker...')
        let caveId = cave.getPopup()._content.match(idExpr)
        if (!caveId) {
          console.warn(`Unable to parse cave ID from: ${cave.getPopup()._content}`)
          return
        }
        // console.log(`Found Cave ID: ${caveId[1]}`)
        try {
          if (!fromSocket) {
            await axios.delete(`${scheme}://${baseAPIUrl}/api/v1/user/${this.user.id}/game_session/${this.selectedSessionId}/marker/${caveId[1]}`)
          }
          for (let i = 0; i < this.user.game_sessions.length; i++) {
            if (this.user.game_sessions[i].id.toString() === this.selectedSessionId) {
              // console.log('Found Game Session')
              for (let x = 0; x < this.user.game_sessions[i].markers.length; x++) {
                // console.log(`Checking Marker ID: ${this.user.game_sessions[i].markers[x].id}`)
                if (this.user.game_sessions[i].markers[x].id.toString() === caveId[1]) {
                  this.user.game_sessions[i].markers.splice(x, 1)
                  // console.log('Set Temp Icon')
                  cave.setIcon(cave.tempIcon)
                  break
                }
              }
              break
            }
          }
        } catch (e) {
          console.warn(e)
        }
      }
    },
    created() {
      this.discoverCaves()
      if (this.user.id) {
        this.signIn()
      }
    },
    beforeMount() {

    }
  })

})();
