# OpenLP Control

Control interface for OpenLP services and presentations.

## Installation

```bash
cd packages/openlp_ctrl
poetry install
```

## Example usage

1. Start server
   ```bash
   poetry run openlp_ctrl
   ```

1. Register client (in web page):
   ```javascript
   const remoteCtrl = document.createElement('a');
   document.documentElement.append(remoteCtrl);
   const ws = new WebSocket('ws://localhost:8000/connect/my-client-id');
   ws.onmessage = (event) => {
       if (event.data.startsWith('slide_update:')) {
           const slideId = event.data.split(':')[1];
           console.log('New slide:', slideId);
           remoteCtrl.setAttribute('href', `#${slideId}`);
           remoteCtrl.click();
       }
   };
   ```

1. Set slide
   ```sh
   curl -X POST -H 'Content-Type: application/json' -d '{"id": "123"}' http://localhost:8000/set-slide
   ```
   response will look like
   ```json
   curl -X POST -H 'Content-Type: application/json' -d '{"id": "123"}' http://localhost:8000/set-slide
   {"message":"Slide update sent to all clients","slide_id":"123","clients_notified":1}(openlp-doc-py3.12)
   ```
